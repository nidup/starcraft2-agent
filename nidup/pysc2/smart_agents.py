import math
import numpy as np
from nidup.pysc2.learning.qlearning import QLearningTable, QLearningTableStorage
from nidup.pysc2.learning.game_results import GameResultsTable
from nidup.pysc2.observations import Observations
from nidup.pysc2.smart_orders import Location, BuildBarracks, BuildSupplyDepot, BuildMarine, Attack, NoOrder
from nidup.pysc2.unit_types import UnitTypeIds
from pysc2.agents.base_agent import BaseAgent
from pysc2.lib import features

_PLAYER_RELATIVE = features.SCREEN_FEATURES.player_relative.index
_UNIT_TYPE = features.SCREEN_FEATURES.unit_type.index
_PLAYER_ID = features.SCREEN_FEATURES.player_id.index

_PLAYER_SELF = 1
_PLAYER_HOSTILE = 4
_ARMY_SUPPLY = 5

_TERRAN_COMMANDCENTER = 18
_TERRAN_SUPPLY_DEPOT = 19
_TERRAN_BARRACKS = 21

ACTION_DO_NOTHING = 'donothing'
ACTION_BUILD_SUPPLY_DEPOT = 'buildsupplydepot'
ACTION_BUILD_BARRACKS = 'buildbarracks'
ACTION_BUILD_MARINE = 'buildmarine'
ACTION_ATTACK = 'attack'

smart_actions = [
    ACTION_DO_NOTHING,
    ACTION_BUILD_SUPPLY_DEPOT,
    ACTION_BUILD_BARRACKS,
    ACTION_BUILD_MARINE,
]

for mm_x in range(0, 64):
    for mm_y in range(0, 64):
        if (mm_x + 1) % 32 == 0 and (mm_y + 1) % 32 == 0:
            smart_actions.append(ACTION_ATTACK + '_' + str(mm_x - 16) + '_' + str(mm_y - 16))


class StateBuilder:

    def current_state(self, location: Location, observations: Observations):
        unit_type = observations.screen().unit_type()
        unit_type_ids = UnitTypeIds()
        cc_y, cc_x = (unit_type == unit_type_ids.terran_command_center()).nonzero()
        cc_count = 1 if cc_y.any() else 0
        depot_y, depot_x = (unit_type == unit_type_ids.terran_supply_depot()).nonzero()
        supply_depot_count = int(round(len(depot_y) / 69))
        barracks_y, barracks_x = (unit_type == unit_type_ids.terran_barracks()).nonzero()
        barracks_count = int(round(len(barracks_y) / 137))

        current_state = np.zeros(8)
        current_state[0] = cc_count
        current_state[1] = supply_depot_count
        current_state[2] = barracks_count
        current_state[3] = observations.player().food_army()

        hot_squares = np.zeros(4)
        enemy_y, enemy_x = (observations.minimap().player_relative() == _PLAYER_HOSTILE).nonzero()
        for i in range(0, len(enemy_y)):
            y = int(math.ceil((enemy_y[i] + 1) / 32))
            x = int(math.ceil((enemy_x[i] + 1) / 32))
            hot_squares[((y - 1) * 2) + (x - 1)] = 1

        if not location.command_center_is_top_left():
            hot_squares = hot_squares[::-1]

        for i in range(0, 4):
            current_state[i + 4] = hot_squares[i]

        return current_state


# based on https://itnext.io/build-a-sparse-reward-pysc2-agent-a44e94ba5255
class ReinforcementAgent(BaseAgent):
    def __init__(self):
        super(ReinforcementAgent, self).__init__()

        self.qlearn = QLearningTable(actions=list(range(len(smart_actions))))
        QLearningTableStorage().load(self.qlearn, self.name())

        self.previous_action = None
        self.previous_state = None
        self.move_number = 0
        self.location = None

    def split_action(self, action_id):
        smart_action = smart_actions[action_id]
        x = 0
        y = 0
        if '_' in smart_action:
            smart_action, x, y = smart_action.split('_')
        return (smart_action, x, y)

    def step(self, obs):
        super(ReinforcementAgent, self).step(obs)
        observations = Observations(obs)

        if obs.last():
            reward = obs.reward

            self.qlearn.learn(str(self.previous_state), self.previous_action, reward, 'terminal')
            QLearningTableStorage().save(self.qlearn, self.name())

            self.previous_action = None
            self.previous_state = None

            self.move_number = 0
            game_results = GameResultsTable(self.name())
            game_results.append(observations.reward(), observations.score_cumulative())

            return NoOrder().do_nothing()

        if obs.first():
            self.location = Location(observations)

        if self.move_number == 0:
            self.move_number += 1

            current_state = StateBuilder().current_state(self.location, observations)

            if self.previous_action is not None:
                self.qlearn.learn(str(self.previous_state), self.previous_action, 0, str(current_state))

            rl_action = self.qlearn.choose_action(str(current_state))

            self.previous_state = current_state
            self.previous_action = rl_action

            smart_action, x, y = self.split_action(self.previous_action)

            if smart_action == ACTION_BUILD_BARRACKS:
                return BuildBarracks(self.location).select_scv(observations)

            elif smart_action == ACTION_BUILD_SUPPLY_DEPOT:
                return BuildSupplyDepot(self.location).select_scv(observations)

            elif smart_action == ACTION_BUILD_MARINE:
                return BuildMarine(self.location).select_barracks(observations)

            elif smart_action == ACTION_ATTACK:
                return Attack(self.location).select_army(observations)

        elif self.move_number == 1:
            self.move_number += 1

            smart_action, x, y = self.split_action(self.previous_action)

            if smart_action == ACTION_BUILD_SUPPLY_DEPOT:
                return BuildSupplyDepot(self.location).build(observations)

            elif smart_action == ACTION_BUILD_BARRACKS:
                return BuildBarracks(self.location).build(observations)

            elif smart_action == ACTION_BUILD_MARINE:
                return BuildMarine(self.location).train_marine(observations)

            elif smart_action == ACTION_ATTACK:
                return Attack(self.location).attack_minimap(observations, int(x), int(y))

        elif self.move_number == 2:
            self.move_number = 0

            smart_action, x, y = self.split_action(self.previous_action)

            if smart_action == ACTION_BUILD_SUPPLY_DEPOT:
                return BuildSupplyDepot(self.location).send_scv_to_mineral(observations)

            elif smart_action == ACTION_BUILD_BARRACKS:
                return BuildBarracks(self.location).send_scv_to_mineral(observations)

        return NoOrder().do_nothing()

    def name(self) -> str:
        return __name__ + "." + self.__class__.__name__
