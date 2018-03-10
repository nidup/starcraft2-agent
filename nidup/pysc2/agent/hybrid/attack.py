
import math
import numpy as np
from nidup.pysc2.agent.order import Order
from nidup.pysc2.agent.information import Location, BuildingCounter
from nidup.pysc2.agent.smart.orders import BuildMarine, BuildMarauder, Attack, NoOrder
from nidup.pysc2.wrapper.observations import Observations

_PLAYER_SELF = 1
_PLAYER_HOSTILE = 4

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
        counter = BuildingCounter()

        current_state = np.zeros(8)
        current_state[0] = counter.command_center_count(observations)
        current_state[1] = counter.supply_depots_count(observations)
        current_state[2] = counter.barracks_count(observations)
        current_state[3] = counter.factories_count(observations)
        current_state[4] = counter.techlab_barracks_count(observations)
        current_state[5] = observations.player().food_army()

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