
import math
import numpy as np
from nidup.pysc2.agent.order import Order
from nidup.pysc2.agent.information import Location, BuildingCounter, MinimapEnemyHotSquaresBuilder, EnemyDetector, RaceNames
from nidup.pysc2.agent.smart.orders import BuildMarine, BuildMarauder, NoOrder
from nidup.pysc2.agent.hybrid.attack_order_learning import QLearningAttack
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
            return QLearningAttack(self.location, int(x), int(y))
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
