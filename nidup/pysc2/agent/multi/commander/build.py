
from nidup.pysc2.agent.commander import Commander
from nidup.pysc2.agent.order import Order
from nidup.pysc2.agent.information import BuildingCounter, EnemyDetector
from nidup.pysc2.agent.scripted.camera import CenterCameraOnCommandCenter
from nidup.pysc2.agent.multi.order.common import NoOrder
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.agent.information import Location
from nidup.pysc2.agent.multi.order.common import SmartOrder
from nidup.pysc2.agent.multi.order.build import BuildSupplyDepot, BuildBarrack, BuildRefinery, BuildTechLabBarrack, BuildReactorBarrack
from nidup.pysc2.agent.multi.order.train import BuildMarine, BuildMarauder
from nidup.pysc2.agent.multi.order.research import ResearchCombatShield, ResearchConcussiveShells


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
                BuildReactorBarrack(location, 2),
                BuildReactorBarrack(location, 3),
                BuildSupplyDepot(location),
                ResearchConcussiveShells(location),
            ]
        )

    # https://lotv.spawningtool.com/build/65735/
    def create3RaxRushTvXWithFirstUnitsPush(self, location: Location) -> OrderedBuildOrder:
        return OrderedBuildOrder(
            location,
            "3 Rax rush - TvX All-In - With Former Push",
            [
                BuildSupplyDepot(location),
                BuildRefinery(location, 1),
                BuildBarrack(location),
                BuildSupplyDepot(location),
                BuildBarrack(location),
                BuildTechLabBarrack(location, 1),
                BuildBarrack(location),
                ResearchCombatShield(location),
                BuildMarauder(location),
                BuildReactorBarrack(location, 2),
                BuildReactorBarrack(location, 3),
                BuildSupplyDepot(location),
                BuildMarauder(location),
                BuildMarine(location),
                BuildMarine(location),
                BuildMarauder(location),
                BuildMarine(location),
                BuildMarine(location),
                BuildMarine(location),
                BuildMarine(location),
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


class BuildOrderCommander(Commander):

    def __init__(self, location: Location, agent_name: str, enemy_detector: EnemyDetector):
        Commander.__init__(self)
        self.location = location
        self.agent_name = agent_name
        self.enemy_detector = enemy_detector
        self.build_orders = BuildOrderFactory().create3RaxRushTvXWithFirstUnitsPush(location)
        self.current_order = None

    def order(self, observations: Observations)-> Order:
        if self.build_orders.finished(observations):
            return self._extra_supply_depots(observations)
        elif self.current_order and self.current_order.done(observations):
            self.current_order = None
            return CenterCameraOnCommandCenter(self.location)
        elif self.current_order and not self.current_order.done(observations):
            return self.current_order
        elif not self.current_order:
            order = self.build_orders.current(observations)
            if order.doable(observations):
                self.current_order = order
                return self.current_order
        return NoOrder()

    def build_is_finished(self, observations: Observations) -> bool:
        return self.build_orders.finished(observations)

    def _extra_supply_depots(self, observations: Observations) -> Order:
        counter = BuildingCounter()
        expectMore = 8 > counter.supply_depots_count(observations)
        supplyAlmostFull = observations.player().food_cap() - observations.player().food_used() <= 2
        if expectMore and supplyAlmostFull:
            return BuildSupplyDepot(self.location)
        else:
            return NoOrder()
