
from nidup.pysc2.information import BaseLocation, StepIndex
from nidup.pysc2.production.build import OrdersSequence, BuildSupplyDepot, BuildFactory, BuildRefinery, BuildBarracks, BuildTechLabBarracks, MorphOrbitalCommand
from nidup.pysc2.production.train import OrdersRepetition, TrainMarine, TrainMarauder, PushWithArmy


# cf http://liquipedia.net/starcraft2/MMM_Timing_Push
class TerranMMMTimingPushBuildOrder:

    step_index = None
    # scout
    # collect
    build_orders: None
    attack_orders: None

    def __init__(self, base_location: BaseLocation):
        self.step_index = StepIndex()
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
            ]
        )
        self.attack_orders = OrdersRepetition(
            [
                # Constant Marauder and Marine
                TrainMarine(base_location, 4),
                TrainMarauder(base_location, 3),
                # Research Stimpack
                # Switch Starport Reactor
                # Build 2 Medivacs
                # NoOrder(base_location)
                PushWithArmy(base_location)
            ]
        )

        # TEST
        #self.build_orders = OrdersSequence(
        #    [
        #        BuildRefinery(base_location),
        #    ]
        #)
        #self.attack_orders = OrdersRepetition(
        #    [
        #        SendSCVToRefinery(base_location),
        #    ]
        #)

    def step(self, observations):
        self.step_index.increment_step()
        if not self.build_orders.finished(observations):
            current_order = self.build_orders.current(observations)
            return current_order.execute(observations)
        else:
            current_order = self.attack_orders.current(observations)
            return current_order.execute(observations)

