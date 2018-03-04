
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.agent.order import Order
from nidup.pysc2.agent.commander import Commander
from nidup.pysc2.agent.scripted.information import BaseLocation
from nidup.pysc2.agent.scripted.build import OrdersSequence, CenterCameraOnCommandCenter, BuildSupplyDepot, BuildFactory, BuildRefinery, BuildBarracks, BuildTechLabBarracks, MorphOrbitalCommand
from nidup.pysc2.agent.scripted.train import OrdersRepetition, TrainMarine, TrainMarauder, PushWithArmy
from nidup.pysc2.agent.scripted.scout import Scouting
from nidup.pysc2.wrapper.actions import TerranActions


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


class GameCommander(Commander):

    # collect
    scout_commander = None
    production_commander = None
    army_commander = None
    current_commander = None
    current_order = None

    def __init__(self, base_location: BaseLocation):
        Commander.__init__(self)
        self.scout_commander = ScoutingCommander(base_location)
        self.production_commander = ProductionCommander(base_location)
        self.army_commander = ArmyCommander(base_location)
        self.current_commander = self.scout_commander

    # TODO if NoOrder, move to next commander to avoid No Op
    def order(self, observations: Observations)-> Order:
        if observations.first():
            self.current_order = self.current_commander.order(observations)
        elif self.current_order.done(observations):
            if self.current_commander == self.scout_commander:
                self.current_commander = self.production_commander
            elif self.current_commander == self.production_commander:
                self.current_commander = self.army_commander
            elif self.current_commander == self.army_commander:
                self.current_commander = self.scout_commander
            self.current_order = self.current_commander.order(observations)
        #print(self.current_order)
        return self.current_order


class ScoutingCommander(Commander):

    scouting_order = None

    def __init__(self, base_location: BaseLocation, looping: bool = False):
        Commander.__init__(self)
        self.scouting_order = Scouting(base_location, looping)

    def order(self, observations: Observations) -> Order:
        if self.scouting_order.done(observations):
            return NoOrder()
        else:
            return self.scouting_order


class ProductionCommander(Commander):

    build_orders: None
    base_location = None

    def __init__(self, base_location: BaseLocation):
        Commander.__init__(self)
        self.base_location = base_location
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
            if not self.base_location.camera_centered_on_command_center(observations.screen()):
                current_order = CenterCameraOnCommandCenter(self.base_location)
            else:
                current_order = self.build_orders.current(observations)
            return current_order
        else:
            return NoOrder()


class ArmyCommander(Commander):

    attack_orders: None

    def __init__(self, base_location: BaseLocation):
        Commander.__init__(self)
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
