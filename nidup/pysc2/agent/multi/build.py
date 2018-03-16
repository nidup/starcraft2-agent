
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.agent.information import Location, BuildingCounter
from nidup.pysc2.agent.multi.orders import SmartOrder, BuildSupplyDepot, BuildBarrack, BuildRefinery, BuildFactory, NoOrder, BuildTechLabBarrack, BuildReactorBarrack, ResearchCombatShield, ResearchConcussiveShells, BuildMarine, BuildMarauder


class BuildOrder:

    def __init__(self, location: Location):
        self.location = location
        self.current_order = BuildSupplyDepot(self.location) # as a Terran, you need to start by this
        self.expected_supply_depot = 8 # 2 last can block a vcs against minerals when playing bottom down
        self.expected_barracks = 4
        self.expected_refineries = 1
        self.expected_factories = 1 # second one is not buildable when playing bottom down
        self.expected_techlab_barrack = 1
        self.expected_reactor_barrack = 1

    def current(self, observations: Observations) -> SmartOrder:
        counter = BuildingCounter()
        if not self.current_order.done(observations) and not isinstance(self.current_order, NoOrder):
            return self.current_order
        elif self.expected_refineries == 1 and self.expected_refineries > counter.refineries_count(observations):
            self.current_order = BuildRefinery(self.location, 1)
        elif self.expected_refineries == 2 and 0 == counter.refineries_count(observations):
            self.current_order = BuildRefinery(self.location, 1)
        elif self.expected_refineries == 2 and 1 == counter.refineries_count(observations):
            self.current_order = BuildRefinery(self.location, 2)
        elif self.missing_barracks(observations, counter):
            self.current_order = BuildBarrack(self.location)
        elif self.missing_supply_depot(observations, counter):
            self.current_order = BuildSupplyDepot(self.location)
        elif self.expected_factories > counter.factories_count(observations):
            self.current_order = BuildFactory(self.location)
        elif self.expected_techlab_barrack > counter.techlab_barracks_count(observations):
            self.current_order = BuildTechLabBarrack(self.location, 1)
        elif self.expected_reactor_barrack > counter.reactor_barracks_count(observations):
            self.current_order = BuildReactorBarrack(self.location, 2)
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


class OrderedBuildOrder:

    def __init__(self, location: Location, name: str, ordered_orders: []):
        self.location = location
        self.name = name
        self.current_order = None
        self.current_order_index = 0
        self.ordered_orders = ordered_orders

    def current(self, observations: Observations) -> SmartOrder:
        if not self.current_order:
            self._next_order()
        elif self.current_order.done(observations):
            self._next_order()
        # TODO if not doable??
        # print(self.current_order)
        return self.current_order

    def finished(self, observations: Observations) -> bool:
        current_order_done = self.current_order and self.current_order.done(observations)
        is_last_order = self.current_order_index == len(self.ordered_orders)
        return current_order_done and is_last_order

    def _next_order(self):
        self.current_order = self.ordered_orders[self.current_order_index]
        self.current_order_index = self.current_order_index + 1


class BuildOrderFactory:

    # https://lotv.spawningtool.com/build/65735/
    def create3RaxRushTvX(self, location: Location) -> OrderedBuildOrder:
        return OrderedBuildOrder(
            location,
            "3 Rax rush - TvX All-In",
            [
                BuildSupplyDepot(location),
                BuildRefinery(location, 1),
                BuildBarrack(location),
                BuildSupplyDepot(location),
                BuildBarrack(location),
                BuildTechLabBarrack(location, 1),
                BuildBarrack(location),
                ResearchCombatShield(location),
                #BuildMarauder(location),
                BuildReactorBarrack(location, 2),
                BuildReactorBarrack(location, 3),
                BuildSupplyDepot(location),
                #BuildMarauder(location),
                #BuildMarine(location),
                #BuildMarine(location),
                #BuildMarauder(location),
                #BuildMarine(location),
                #BuildMarine(location),
                #BuildMarine(location),
                #BuildMarine(location),
                ResearchConcussiveShells(location),

                # bigger timing push
                # BuildMarine(location),
                # BuildMarine(location),
                # BuildMarine(location),
                # BuildMarine(location),
                # BuildMarauder(location),
                # BuildMarauder(location),
                #BuildBarrack(location, 4),
                #BuildReactorBarrack(location, 4), NO REACTOR BUILT WHEN PLAY ON TOP GAME?
            ]
        )
