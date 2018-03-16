
import math
import numpy as np
from nidup.pysc2.agent.commander import Commander
from nidup.pysc2.agent.order import Order
from nidup.pysc2.learning.qlearning import QLearningTable, QLearningTableStorage
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.agent.information import Location
from nidup.pysc2.agent.smart.orders import BuildBarracks, BuildSupplyDepot, BuildMarine, Attack, NoOrder
from nidup.pysc2.wrapper.unit_types import UnitTypeIds

_PLAYER_SELF = 1
_PLAYER_HOSTILE = 4

ACTION_DO_NOTHING = 'donothing'
ACTION_BUILD_SUPPLY_DEPOT = 'buildsupplydepot'
ACTION_BUILD_BARRACKS = 'buildbarracks'
ACTION_BUILD_MARINE = 'buildmarine'
ACTION_ATTACK = 'attack'


class SmartActions:

    def __init__(self, location: Location):
        self.location = location
        self.actions = [
            ACTION_DO_NOTHING,
            ACTION_BUILD_SUPPLY_DEPOT,
            ACTION_BUILD_BARRACKS,
            ACTION_BUILD_MARINE
        ]
        # split the mini-map into four quadrants keep the action space small to make it easier for the agent to learn
        attack_actions = []
        for mm_x in range(0, 64):
            for mm_y in range(0, 64):
                if (mm_x + 1) % 32 == 0 and (mm_y + 1) % 32 == 0:
                    attack_actions.append(ACTION_ATTACK + '_' + str(mm_x - 16) + '_' + str(mm_y - 16))
        # remove the player's base quadrant
        del attack_actions[0]
        # keep only enemy's base 1 and base 2 quadrants (natural expansion)
        del attack_actions[1]
        self.actions = self.actions + attack_actions

    def all(self) -> []:
        return self.actions

    def order(self, action_id: str) -> Order:
        smart_action, x, y = self._split_action(action_id)
        if smart_action == ACTION_BUILD_BARRACKS:
            max_barracks = 2
            return BuildBarracks(self.location, max_barracks)
        elif smart_action == ACTION_BUILD_SUPPLY_DEPOT:
            max_supplies = 2
            return BuildSupplyDepot(self.location, max_supplies)
        elif smart_action == ACTION_BUILD_MARINE:
            return BuildMarine(self.location)
        elif smart_action == ACTION_ATTACK:
            return Attack(self.location, int(x), int(y))
        elif smart_action == ACTION_DO_NOTHING:
            return NoOrder()
        else:
            raise Exception('The smart action ' + smart_action + " is unknown")

    def _split_action(self, action_id):
        smart_action = self.actions[action_id]
        x = 0
        y = 0
        if '_' in smart_action:
            smart_action, x, y = smart_action.split('_')
        return smart_action, x, y


class StateBuilder:

    def build_state(self, location: Location, observations: Observations) -> []:
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
class QLearningCommander(Commander):

    def __init__(self, agent_name: str):
        super(Commander, self).__init__()
        self.agent_name = agent_name
        self.smart_actions = None
        self.qlearn = None
        self.previous_action = None
        self.previous_state = None
        self.previous_order = None
        self.location = None

    def order(self, observations: Observations, step_index: int)-> Order:
        if observations.last():
            self.qlearn.learn(str(self.previous_state), self.previous_action, observations.reward(), 'terminal')
            QLearningTableStorage().save(self.qlearn, self.agent_name)

            self.previous_action = None
            self.previous_state = None
            self.previous_order = None

            return NoOrder()

        elif observations.first():
            self.location = Location(observations)
            self.smart_actions = SmartActions(self.location)
            self.qlearn = QLearningTable(actions=list(range(len(self.smart_actions.all()))))
            QLearningTableStorage().load(self.qlearn, self.agent_name)

        if not self.previous_order or self.previous_order.done(observations):

            current_state = StateBuilder().build_state(self.location, observations)

            if self.previous_action is not None:
                self.qlearn.learn(str(self.previous_state), self.previous_action, 0, str(current_state))

            rl_action = self.qlearn.choose_action(str(current_state))

            self.previous_state = current_state
            self.previous_action = rl_action
            self.previous_order = self.smart_actions.order(rl_action)

        return self.previous_order
