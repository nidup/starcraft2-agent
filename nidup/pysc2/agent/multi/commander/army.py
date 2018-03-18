
import numpy as np
from nidup.pysc2.agent.commander import Commander
from nidup.pysc2.learning.qlearning import QLearningTable, QLearningTableStorage
from nidup.pysc2.agent.order import Order
from nidup.pysc2.agent.information import Location, BuildingCounter, MinimapEnemyHotSquaresBuilder, EnemyDetector, RaceNames
from nidup.pysc2.agent.multi.order.common import NoOrder
from nidup.pysc2.agent.multi.order.attack import DumbAttack
from nidup.pysc2.agent.multi.order.train import BuildMarine, BuildMarauder
from nidup.pysc2.wrapper.observations import Observations

ACTION_DO_NOTHING = 'donothing'
ACTION_BUILD_MARINE = 'buildmarine'
ACTION_BUILD_MARAUDER = 'buildmarauder'
ACTION_ATTACK = 'attack'


class SmartActions:

    def __init__(self, location: Location):
        self.location = location
        self.actions = [
            ACTION_DO_NOTHING,
            ACTION_BUILD_MARINE,
            ACTION_BUILD_MARAUDER
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
        if smart_action == ACTION_BUILD_MARINE:
            return BuildMarine(self.location)
        elif smart_action == ACTION_BUILD_MARAUDER:
            return BuildMarauder(self.location)
        elif smart_action == ACTION_ATTACK:
            return DumbAttack(self.location, int(x), int(y))
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

    def build_state(self, location: Location, observations: Observations, enemy_detector: EnemyDetector) -> []:
        counter = BuildingCounter()

        base_state_items_length = 8
        hot_squares_length = 4
        current_state_length = base_state_items_length + hot_squares_length

        current_state = np.zeros(current_state_length)
        current_state[0] = counter.command_center_count(observations)
        current_state[1] = counter.supply_depots_count(observations)
        current_state[2] = counter.barracks_count(observations)
        current_state[3] = counter.factories_count(observations)
        current_state[4] = counter.techlab_barracks_count(observations)
        current_state[5] = counter.reactor_barracks_count(observations)
        current_state[6] = self._enemy_race_id(enemy_detector)
        current_state[7] = observations.player().food_army()

        hot_squares = MinimapEnemyHotSquaresBuilder().minimap_four_squares(observations, location)
        for i in range(0, hot_squares_length):
            current_state[i + base_state_items_length] = hot_squares[i]

        return current_state

    def _enemy_race_id(self, enemy_detector: EnemyDetector) -> int:
        race = enemy_detector.race()
        name_to_id = {
            RaceNames().unknown(): 0,
            RaceNames().protoss(): 1,
            RaceNames().terran(): 2,
            RaceNames().zerg(): 3,
        }
        return name_to_id[race]


class QLearningAttackCommander(Commander):

    def __init__(self, location: Location, agent_name: str, enemy_detector: EnemyDetector):
        super(Commander, self).__init__()
        self.location = location
        self.agent_name = agent_name
        self.enemy_detector = enemy_detector
        self.smart_actions = None
        self.qlearn = None
        self.previous_action = None
        self.previous_state = None
        self.previous_order = None

        self.smart_actions = SmartActions(self.location)
        self.qlearn = QLearningTable(actions=list(range(len(self.smart_actions.all()))))
        QLearningTableStorage().load(self.qlearn, self.agent_name)

    def order(self, observations: Observations, step_index: int)-> Order:
        if observations.last():
            self.qlearn.learn(str(self.previous_state), self.previous_action, observations.reward(), 'terminal')
            QLearningTableStorage().save(self.qlearn, self.agent_name)
            self.previous_action = None
            self.previous_state = None
            self.previous_order = None
            return NoOrder()

        if not self.previous_order or self.previous_order.done(observations):
            current_state = StateBuilder().build_state(self.location, observations, self.enemy_detector)
            if self.previous_action is not None:
                self.qlearn.learn(str(self.previous_state), self.previous_action, 0, str(current_state))
            rl_action = self.qlearn.choose_action(str(current_state))
            self.previous_state = current_state
            self.previous_action = rl_action
            self.previous_order = self.smart_actions.order(rl_action)

        return self.previous_order
