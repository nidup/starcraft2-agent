
import math
import numpy as np
from nidup.pysc2.agent.commander import Commander
from nidup.pysc2.agent.order import Order
from nidup.pysc2.learning.qlearning import QLearningTable, QLearningTableStorage
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.agent.information import Location
from nidup.pysc2.agent.scripted.camera import CenterCameraOnCommandCenter
from nidup.pysc2.agent.smart.orders import BuildSupplyDepot, BuildBarrack, BuildRefinery, BuildFactory, BuildMarine, BuildMarauder, Attack, NoOrder, PrepareSCVControlGroupsOrder, BuildTechLabBarrack
from nidup.pysc2.wrapper.unit_types import UnitTypeIds

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


class BuildingCounter:

    def command_center_count(self, observations: Observations) -> int:
        unit_type = observations.screen().unit_type()
        unit_type_ids = UnitTypeIds()
        cc_y, cc_x = (unit_type == unit_type_ids.terran_command_center()).nonzero()
        cc_count = 1 if cc_y.any() else 0
        return cc_count

    def supply_depots_count(self, observations: Observations) -> int:
        unit_type = observations.screen().unit_type()
        unit_type_ids = UnitTypeIds()
        depot_y, depot_x = (unit_type == unit_type_ids.terran_supply_depot()).nonzero()
        supply_depot_count = int(round(len(depot_y) / 69))
        return supply_depot_count

    def barracks_count(self, observations: Observations) -> int:
        unit_type = observations.screen().unit_type()
        unit_type_ids = UnitTypeIds()
        barracks_y, barracks_x = (unit_type == unit_type_ids.terran_barracks()).nonzero()
        barracks_count = int(round(len(barracks_y) / 137))
        return barracks_count

    def techlab_barracks_count(self, observations: Observations) -> int:
        unit_type = observations.screen().unit_type()
        unit_type_ids = UnitTypeIds()
        techlabs_y, tachlabs_x = (unit_type == unit_type_ids.terran_barracks_techlab()).nonzero()
        if techlabs_y.any():
            return 1
        return 0

    def refineries_count(self, observations: Observations) -> int:
        unit_type = observations.screen().unit_type()
        unit_type_ids = UnitTypeIds()
        unit_y, unit_x = (unit_type == unit_type_ids.terran_refinery()).nonzero()
        units_count = int(round(len(unit_y) / 97))
        return units_count

    def factories_count(self, observations: Observations) -> int:
        unit_type = observations.screen().unit_type()
        unit_type_ids = UnitTypeIds()
        factories_y, factories_x = (unit_type == unit_type_ids.terran_factory()).nonzero()
        factories_count = int(round(len(factories_y) / 137))
        return factories_count


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


class HybridGameCommander(Commander):

    def __init__(self, base_location: Location, agent_name: str):
        Commander.__init__(self)
        self.control_group_order = PrepareSCVControlGroupsOrder(base_location)
        self.build_order_commander = BuildOrderCommander(base_location, agent_name)
        self.attack_commander = QLearningAttackCommander(base_location, agent_name)
        self.build_order_finished = False

    def order(self, observations: Observations)-> Order:

        # TODO: send SCV back to minerals?
        if not self.control_group_order.done(observations):
            return self.control_group_order
        elif not self.build_order_finished:
            order = self.build_order_commander.order(observations)
            if isinstance(order, NoOrder):
                self.build_order_finished = True
            else:
                return order

        return self.attack_commander.order(observations)


class BuildOrder:

    def __init__(self, location: Location):
        self.location = location
        self.current_order = BuildSupplyDepot(self.location)
        self.expected_supply_depot = 8 # 2 last can block a vcs against minerals when playing bottom down
        self.expected_barracks = 4
        self.expected_refineries = 2
        self.expected_factories = 1 # second one is not buildable when playing bottom down
        self.expected_techlab_barrack = 1

    def current(self, observations: Observations) -> Order:
        counter = BuildingCounter()
        if not self.current_order.done(observations):
            return self.current_order
        elif counter.supply_depots_count(observations) < self.expected_supply_depot:
            self.current_order = BuildSupplyDepot(self.location)
        elif counter.barracks_count(observations) < self.expected_barracks:
            self.current_order = BuildBarrack(self.location)
        elif counter.refineries_count(observations) < self.expected_refineries:
            self.current_order = BuildRefinery(self.location)
        elif counter.factories_count(observations) < self.expected_factories:
            self.current_order = BuildFactory(self.location)
        elif counter.techlab_barracks_count(observations) < self.expected_techlab_barrack:
            self.current_order = BuildTechLabBarrack(self.location)
        else:
            self.current_order = NoOrder()
        return self.current_order

    def finished(self, observations: Observations) -> bool:
        counter = BuildingCounter()
        supply_ok = counter.supply_depots_count(observations) == self.expected_supply_depot
        barracks_ok = counter.barracks_count(observations) == self.expected_barracks
        refineries_ok = counter.refineries_count(observations) == self.expected_refineries
        factories_ok = counter.factories_count(observations) == self.expected_factories
        techlab_barracks_ok = counter.techlab_barracks_count(observations) == self.expected_techlab_barrack
        return supply_ok and barracks_ok and refineries_ok and factories_ok and techlab_barracks_ok


class BuildOrderCommander(Commander):

    def __init__(self, location: Location, agent_name: str):
        Commander.__init__(self)
        self.location = location
        self.agent_name = agent_name
        self.build_orders = BuildOrder(self.location)
        self.current_order = None

    def order(self, observations: Observations)-> Order:
        if self.build_orders.finished(observations):
            #print(self.current_order)
            return NoOrder()
        elif self.current_order and self.current_order.done(observations):
            #print(self.current_order)
            #camera_y, camera_x = self.location.current_visible_minimap_left_corner(observations.minimap())
            #print("center camera from " + str(camera_x) + " " + str(camera_y) + " base top left " + str(self.location.command_center_is_top_left()))
            self.current_order = None
            return CenterCameraOnCommandCenter(self.location)
        else:
            self.current_order = self.build_orders.current(observations)
            #print(self.current_order)
            return self.current_order


class QLearningAttackCommander(Commander):

    def __init__(self, location: Location, agent_name: str):
        super(Commander, self).__init__()
        self.location = location
        self.agent_name = agent_name
        self.smart_actions = None
        self.qlearn = None
        self.previous_action = None
        self.previous_state = None
        self.previous_order = None
        self.location = location

        self.smart_actions = SmartActions(self.location)
        self.qlearn = QLearningTable(actions=list(range(len(self.smart_actions.all()))))
        QLearningTableStorage().load(self.qlearn, self.agent_name)

    def order(self, observations: Observations)-> Order:
        if observations.last():
            self.qlearn.learn(str(self.previous_state), self.previous_action, observations.reward(), 'terminal')
            QLearningTableStorage().save(self.qlearn, self.agent_name)

            self.previous_action = None
            self.previous_state = None
            self.previous_order = None

            return NoOrder()

        if not self.previous_order or self.previous_order.done(observations):

            current_state = StateBuilder().build_state(self.location, observations)

            if self.previous_action is not None:
                self.qlearn.learn(str(self.previous_state), self.previous_action, 0, str(current_state))

            rl_action = self.qlearn.choose_action(str(current_state))

            self.previous_state = current_state
            self.previous_action = rl_action
            self.previous_order = self.smart_actions.order(rl_action)

        return self.previous_order
