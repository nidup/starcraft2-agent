
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.agent.hybrid.information import Location
from nidup.pysc2.agent.hybrid.orders import SmartOrder, BuildSupplyDepot, BuildBarrack, BuildRefinery, BuildTechLabBarrack, BuildReactorBarrack, ResearchCombatShield, ResearchConcussiveShells


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
