
from nidup.pysc2.agent.order import Order
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.agent.information import Location, BuildingCounter
from nidup.pysc2.agent.smart.orders import BuildSupplyDepot, BuildBarrack, BuildRefinery, BuildFactory, NoOrder, BuildTechLabBarrack


class BuildOrder:

    def __init__(self, location: Location):
        self.location = location
        self.current_order = BuildSupplyDepot(self.location) # as a Terran, you need to start by this
        self.expected_supply_depot = 8 # 2 last can block a vcs against minerals when playing bottom down
        self.expected_barracks = 4
        self.expected_refineries = 1
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
