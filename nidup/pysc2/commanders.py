
from nidup.pysc2.observations import Observations
from nidup.pysc2.order import Order
from nidup.pysc2.information import BaseLocation, StepIndex
from nidup.pysc2.production.build import OrdersSequence, BuildSupplyDepot, BuildFactory, BuildRefinery, BuildBarracks, BuildTechLabBarracks, MorphOrbitalCommand
from nidup.pysc2.production.train import OrdersRepetition, TrainMarine, TrainMarauder, PushWithArmy
from nidup.pysc2.actions import TerranActions


class NoOrder(Order):

    is_done = False
    actions = None

    def __init__(self):
        Order.__init__(self)
        self.actions = TerranActions()

    def done(self, observations: Observations):
        return self.is_done

    def execute(self, obs: Observations):
        self.is_done = True
        return self.actions.no_op()


class GameCommander:

    step_index = None
    # collect
    # scout
    production_commander = None
    army_commander = None
    current_commander = None
    current_order = None

    def __init__(self, base_location: BaseLocation):
        self.production_commander = ProductionCommander(base_location)
        self.army_commander = ArmyCommander(base_location)
        self.current_commander = self.production_commander
        self.step_index = StepIndex()

    def order(self, observations: Observations)-> Order:
        self.step_index.increment_step()
        if not self.current_order:
            self.current_order = self.current_commander.order(observations)
        elif self.current_order.done(observations):
            if self.current_commander == self.production_commander:
                self.current_commander = self.army_commander
            else:
                self.current_commander = self.production_commander
            self.current_order = self.current_commander.order(observations)
        return self.current_order


class ProductionCommander:

    build_orders: None

    def __init__(self, base_location: BaseLocation):
        # cf http://liquipedia.net/starcraft2/MMM_Timing_Push
        self.build_orders = OrdersSequence(
            [
                BuildSupplyDepot(base_location, 0, 15),
                BuildBarracks(base_location, 20, 0),
                BuildRefinery(base_location),
                #SendSCVToRefinery(base_location),
                MorphOrbitalCommand(base_location),
                #TrainMarine(base_location, 3), TODO: no more mixes of Build & Train Order
                BuildSupplyDepot(base_location, 0, 30),
                BuildFactory(base_location, 20, 20),
                # Barracks (2)
                # Refinery (2)
                BuildTechLabBarracks(base_location),
                # Starport
                # Reactor on Factory
                # Timing Push
                # Research Stimpack
                # Switch Starport Reactor
                # Build 2 Medivacs
                # NoOrder(base_location)
            ]
        )

    def order(self, observations: Observations)-> Order:
        if not self.build_orders.finished(observations):
            current_order = self.build_orders.current(observations)
            return current_order
        else:
            return NoOrder()


class ArmyCommander:

    attack_orders: None

    def __init__(self, base_location: BaseLocation):
        self.attack_orders = OrdersRepetition(
            [
                # Constant Marauder and Marine
                TrainMarine(base_location, 4),
                TrainMarauder(base_location, 3),
                PushWithArmy(base_location)
            ]
        )

    def order(self, observations: Observations)-> Order:
        current = self.attack_orders.current(observations)
        if current.executable(observations):
            return current
        else:
            return NoOrder()