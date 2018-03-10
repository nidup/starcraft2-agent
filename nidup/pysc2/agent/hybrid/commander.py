
from nidup.pysc2.agent.commander import Commander
from nidup.pysc2.agent.order import Order
from nidup.pysc2.learning.qlearning import QLearningTable, QLearningTableStorage
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.agent.information import Location, BuildingCounter
from nidup.pysc2.agent.scripted.camera import CenterCameraOnCommandCenter
from nidup.pysc2.agent.smart.orders import BuildSupplyDepot, BuildBarrack, BuildRefinery, BuildFactory, NoOrder, PrepareSCVControlGroupsOrder, BuildTechLabBarrack
from nidup.pysc2.agent.hybrid.attack import SmartActions, StateBuilder


class HybridGameCommander(Commander):

    def __init__(self, base_location: Location, agent_name: str):
        Commander.__init__(self)
        self.control_group_order = PrepareSCVControlGroupsOrder(base_location)
        self.build_order_commander = BuildOrderCommander(base_location, agent_name)
        self.attack_commander = QLearningAttackCommander(base_location, agent_name)

    def order(self, observations: Observations)-> Order:
        if not self.control_group_order.done(observations):
            return self.control_group_order
        else:
            order = self.build_order_commander.order(observations)
            if not isinstance(order, NoOrder):
                return order

        return self.attack_commander.order(observations)


class BuildOrder:

    def __init__(self, location: Location):
        self.location = location
        self.current_order = BuildSupplyDepot(self.location) # as a Terran, you need to start by this
        self.expected_supply_depot = 8 # 2 last can block a vcs against minerals when playing bottom down
        self.expected_barracks = 4
        self.expected_refineries = 2
        self.expected_factories = 1 # second one is not buildable when playing bottom down
        self.expected_techlab_barrack = 1

    def current(self, observations: Observations) -> Order:
        counter = BuildingCounter()
        if not self.current_order.done(observations) and not isinstance(self.current_order, NoOrder):
            return self.current_order
        elif self.missing_barracks(observations, counter):
            self.current_order = BuildBarrack(self.location)
        elif self.missing_supply_depot(observations, counter):
            self.current_order = BuildSupplyDepot(self.location)
        elif self.expected_refineries > counter.refineries_count(observations):
            self.current_order = BuildRefinery(self.location)
        elif self.expected_factories > counter.factories_count(observations):
            self.current_order = BuildFactory(self.location)
        elif self.expected_techlab_barrack > counter.techlab_barracks_count(observations):
            self.current_order = BuildTechLabBarrack(self.location)
        else:
            self.current_order = NoOrder()
        return self.current_order

    def missing_supply_depot(self, observations: Observations, counter: BuildingCounter) -> bool:
        expectMore = self.expected_supply_depot > counter.supply_depots_count(observations)
        supplyAlmostFull = observations.player().food_cap() - observations.player().food_used() <= 4
        buildingOne = isinstance(self.current_order, BuildSupplyDepot)
        # but still build several in a row, needs to detect if a supply building is in progress
        return expectMore and supplyAlmostFull and not buildingOne

    def missing_barracks(self, observations: Observations, counter: BuildingCounter) -> bool:
        expectMore = self.expected_barracks > counter.barracks_count(observations)
        buildingOne = isinstance(self.current_order, BuildBarrack)
        return expectMore and not buildingOne

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
