
from pysc2.lib import actions
from nidup.pysc2.observations import Observations, ScreenFeatures
from sklearn.cluster import KMeans
import math

# Functions
_NOOP = actions.FUNCTIONS.no_op.id
_BUILD_SUPPLYDEPOT = actions.FUNCTIONS.Build_SupplyDepot_screen.id
_BUILD_BARRACKS = actions.FUNCTIONS.Build_Barracks_screen.id
_BUILD_TECHLAB_BARRACKS = actions.FUNCTIONS.Build_TechLab_screen.id
_BUILD_REFINERY = actions.FUNCTIONS.Build_Refinery_screen.id
_MORPH_ORBITAL_COMMAND = actions.FUNCTIONS.Morph_OrbitalCommand_quick.id
_BUILD_FACTORY = actions.FUNCTIONS.Build_Factory_screen.id

_SELECT_POINT = actions.FUNCTIONS.select_point.id
_SELECT_IDLE_WORKER = actions.FUNCTIONS.select_idle_worker.id
_RALLY_UNITS_MINIMAP = actions.FUNCTIONS.Rally_Units_minimap.id
_SELECT_ARMY = actions.FUNCTIONS.select_army.id
_TRAIN_MARINE = actions.FUNCTIONS.Train_Marine_quick.id
_TRAIN_MARAUDER = actions.FUNCTIONS.Train_Marauder_quick.id
_ATTACK_MINIMAP = actions.FUNCTIONS.Attack_minimap.id
_ATTACK_SCREEN = actions.FUNCTIONS.Attack_screen.id
_MOVE_SCREEN = actions.FUNCTIONS.Move_screen.id

# Unit IDs cf https://github.com/Blizzard/s2client-api/blob/master/include/sc2api/sc2_typeenums.h
_TERRAN_BARRACKS = 21
_TERRAN_FACTORY = 27
_TERRAN_COMMANDCENTER = 18
_TERRAN_ORBITALCOMMAND = 132
_TERRAN_SUPPLYDEPOT = 19
_TERRAN_SCV = 45
_TERRAN_REFINERY = 20
_NEUTRAL_VESPENE_GEYSER = 342
_NEUTRAL_MINERALFIELD = 341

# Parameters
_NOT_QUEUED = [0]
_QUEUED = [1]


# cf http://liquipedia.net/starcraft2/MMM_Timing_Push
class MMMTimingPushBuildOrder:

    build_orders: None
    attack_orders: None

    def __init__(self, base_top_left):
        base_location = BaseLocation(base_top_left)
        self.build_orders = OrdersSequence(
            [
                BuildSupplyDepot(base_location, 0, 15),
                BuildBarracks(base_location, 20, 0),
                BuildRefinery(base_location),
                #SendSCVToRefinery(base_location),
                MorphOrbitalCommand(base_location),
                TrainMarine(base_location, 3),
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
                TrainMarauder(base_location, 4),
                TrainMarine(base_location, 20),
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

    def action(self, observations):
        if not self.build_orders.finished(observations):
            current_order = self.build_orders.current(observations)
            return current_order.execute(observations)
        else:
            current_order = self.attack_orders.current(observations)
            return current_order.execute(observations)


class BaseLocation:

    base_top_left = None

    def __init__(self, base_top_left):
        self.base_top_left = base_top_left

    def top_left(self):
        return self.base_top_left

    def transform_location(self, x, x_distance, y, y_distance):
        if not self.base_top_left:
            return [x - x_distance, y - y_distance]

        return [x + x_distance, y + y_distance]

    def locate_command_center(self, screen: ScreenFeatures):
        unit_type = screen.unit_type()
        unit_y, unit_x = (unit_type == _TERRAN_COMMANDCENTER).nonzero()
        if not unit_x.any():
            unit_y, unit_x = (unit_type == _TERRAN_ORBITALCOMMAND).nonzero()
        return unit_y, unit_x


class Order:
    base_location = None

    def __init__(self, base_location):
        self.base_location = base_location

    def done(self, observations: Observations):
        raise NotImplementedError("Should be implemented by concrete order")

    def execute(self, observations: Observations):
        raise NotImplementedError("Should be implemented by concrete order")


class OrdersSequence:
    orders = None
    current_order = None
    current_order_index = None

    def __init__(self, orders):
        self.orders = orders
        self.current_order_index = 0
        self.current_order = self.orders[self.current_order_index]

    def current(self, observations: Observations) -> Order:
        print("order" + str(self.current_order_index))
        print(self.current_order)
        if self.current_order.done(observations):
            self._next_order()
        return self.current_order

    def finished(self, observations: Observations) -> bool:
        return self.current_order.done(observations) and self.current_order_index == len(self.orders) - 1

    def _next_order(self):
        self.current_order_index = self.current_order_index + 1
        self.current_order = self.orders[self.current_order_index]


class OrdersRepetition:
    orders = None
    current_order = None
    current_order_index = None

    def __init__(self, orders):
        self.orders = orders
        self.current_order_index = 0
        self.current_order = self.orders[self.current_order_index]

    def current(self, observations: Observations) -> Order:
        print("order" + str(self.current_order_index))
        print(self.current_order)
        if self.current_order.done(observations):
            self._next_order()
        return self.current_order

    def _next_order(self):
        self.current_order_index = self.current_order_index + 1
        if self.current_order_index < len(self.orders):
            self.current_order = self.orders[self.current_order_index]
        else:
            self.current_order_index = 0
            self.current_order = self.orders[self.current_order_index]


class SelectSCV(Order):

    scv_selected = False

    def __init__(self, base_location):
        Order.__init__(self, base_location)

    def done(self, observations: Observations):
        return self.scv_selected

    def execute(self, observations: Observations):
        if not self.scv_selected:
            if observations.player().idle_worker_count() > 0:
                self.scv_selected = True
                return actions.FunctionCall(_SELECT_IDLE_WORKER, [_NOT_QUEUED])
            else:
                unit_type = observations.screen().unit_type()
                unit_y, unit_x = (unit_type == _TERRAN_SCV).nonzero()
                target = [unit_x[0], unit_y[0]]
                self.scv_selected = True
                return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])

        return actions.FunctionCall(_NOOP, [])


class BuildSupplyDepot(Order):

    select_scv_order = False
    supply_depot_built = False
    x_from_base = None
    y_from_base = None

    def __init__(self, base_location, x_from_base, y_from_base):
        Order.__init__(self, base_location)
        self.x_from_base = x_from_base
        self.y_from_base = y_from_base
        self.select_scv_order = SelectSCV(base_location)

    def done(self, observations: Observations):
        return self.supply_depot_built

    def execute(self, observations: Observations):
        if not self.supply_depot_built:
            if not self.select_scv_order.done(observations):
                return self.select_scv_order.execute(observations)
            elif _BUILD_SUPPLYDEPOT in observations.available_actions():
                unit_y, unit_x = self.base_location.locate_command_center(observations.screen())
                target = self.base_location.transform_location(
                    int(unit_x.mean()),
                    self.x_from_base,
                    int(unit_y.mean()),
                    self.y_from_base
                )
                self.supply_depot_built = True
                return actions.FunctionCall(_BUILD_SUPPLYDEPOT, [_NOT_QUEUED, target])
        return actions.FunctionCall(_NOOP, [])


class BuildRefinery(Order):

    select_scv_order = None
    refinery_built = False

    def __init__(self, base_location):
        Order.__init__(self, base_location)
        self.select_scv_order = SelectSCV(base_location)

    def done(self, observations: Observations):
        return self.refinery_built

    def execute(self, observations: Observations):
        if not self.refinery_built:
            if not self.select_scv_order.done(observations):
                return self.select_scv_order.execute(observations)

            # https://itnext.io/how-to-locate-and-select-units-in-pysc2-2bb1c81f2ad3
            elif _BUILD_REFINERY in observations.available_actions():
                unit_type = observations.screen().unit_type()
                vespene_y, vespene_x = (unit_type == _NEUTRAL_VESPENE_GEYSER).nonzero()
                vespene_geyser_count = int(math.ceil(len(vespene_y) / 97))
                units = []
                for i in range(0, len(vespene_y)):
                    units.append((vespene_x[i], vespene_y[i]))
                kmeans = KMeans(vespene_geyser_count)
                kmeans.fit(units)
                vespene1_x = int(kmeans.cluster_centers_[0][0])
                vespene1_y = int(kmeans.cluster_centers_[0][1])
                target = [vespene1_x, vespene1_y]
                self.refinery_built = True
                return actions.FunctionCall(_BUILD_REFINERY, [_NOT_QUEUED, target])
        return actions.FunctionCall(_NOOP, [])


class SendSCVToRefinery(Order):

    select_scv_order = False
    scv_sent_to_refinery = False

    def __init__(self, base_location):
        Order.__init__(self, base_location)
        self.select_scv_order = SelectSCV(base_location)

    def done(self, observations: Observations):
        return self.scv_sent_to_refinery

    def execute(self, observations: Observations):
        if not self.select_scv_order.done(observations):
            return self.select_scv_order.execute(observations)
        elif _MOVE_SCREEN in observations.available_actions():
            unit_type = observations.screen().unit_type()
            unit_y, unit_x = (unit_type == _TERRAN_REFINERY).nonzero()
            if unit_y.any():
                target = [int(unit_x.mean()), int(unit_y.mean())]
                self.scv_sent_to_refinery = True
                return actions.FunctionCall(_MOVE_SCREEN, [_NOT_QUEUED, target])
        return actions.FunctionCall(_NOOP, [])


class BuildArmyBuilding(Order):

    x_from_base = None
    y_from_base = None
    build_action = None
    building_unit_type = None
    select_scv_order = None
    building_built = False
    building_selected = False
    building_rallied = False

    def __init__(self, base_location, x_from_base, y_from_base, build_action, building_unit_type):
        Order.__init__(self, base_location)
        self.x_from_base = x_from_base
        self.y_from_base = y_from_base
        self.build_action = build_action
        self.building_unit_type = building_unit_type
        self.select_scv_order = SelectSCV(base_location)

    def done(self, observations: Observations):
        return self.building_rallied

    def execute(self, observations: Observations):
        if not self.building_built:
            if self.build_action in observations.available_actions():
                unit_y, unit_x = self.base_location.locate_command_center(observations.screen())
                if unit_x.any():
                    target = self.base_location.transform_location(
                        int(unit_x.mean()),
                        self.x_from_base,
                        int(unit_y.mean()),
                        self.y_from_base
                    )
                    self.building_built = True
                    return actions.FunctionCall(self.build_action, [_NOT_QUEUED, target])
            elif not self.select_scv_order.done(observations):
                return self.select_scv_order.execute(observations)
        elif not self.building_rallied:
            if not self.building_selected:
                unit_type = observations.screen().unit_type()
                unit_y, unit_x = (unit_type == self.building_unit_type).nonzero()
                if unit_y.any():
                    target = [int(unit_x.mean()), int(unit_y.mean())]
                    self.building_selected = True
                    return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])
            else:
                self.building_rallied = True
                if self.base_location.top_left():
                    return actions.FunctionCall(_RALLY_UNITS_MINIMAP, [_NOT_QUEUED, [29, 21]])

                return actions.FunctionCall(_RALLY_UNITS_MINIMAP, [_NOT_QUEUED, [29, 46]])
        return actions.FunctionCall(_NOOP, [])


class BuildBarracks(BuildArmyBuilding):

    def __init__(self, base_location, x_from_base, y_from_base):
        BuildArmyBuilding.__init__(self, base_location, x_from_base, y_from_base, _BUILD_BARRACKS, _TERRAN_BARRACKS)


class BuildFactory(BuildArmyBuilding):

    def __init__(self, base_location, x_from_base, y_from_base):
        BuildArmyBuilding.__init__(self, base_location, x_from_base, y_from_base, _BUILD_FACTORY, _TERRAN_FACTORY)


class TrainBarracksUnit(Order):

    amount_trainee = 0
    already_trained = 0
    train_action = None
    barracks_selected = False
    army_selected = False
    army_rallied = False

    def __init__(self, base_location, amount, train_action):
        Order.__init__(self, base_location)
        self.amount_trainee = amount
        self.train_action = train_action

    def done(self, observations: Observations):
        return (self.already_trained >= self.amount_trainee)\
               or (observations.player().food_used() == observations.player().food_cap())

    def execute(self, observations: Observations):
        if self.train_action in observations.available_actions():
            self.already_trained = self.already_trained + 1
            return actions.FunctionCall(self.train_action, [_QUEUED])
        elif not self.barracks_selected:
            unit_type = observations.screen().unit_type()
            unit_y, unit_x = (unit_type == _TERRAN_BARRACKS).nonzero()
            if unit_y.any():
                target = [int(unit_x.mean()), int(unit_y.mean())]
                self.barracks_selected = True
                return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])
        return actions.FunctionCall(_NOOP, [])


class TrainMarine(TrainBarracksUnit):

    def __init__(self, base_location, amount):
        TrainBarracksUnit.__init__(self, base_location, amount, _TRAIN_MARINE)


class TrainMarauder(TrainBarracksUnit):

    def __init__(self, base_location, amount):
        TrainBarracksUnit.__init__(self, base_location, amount, _TRAIN_MARAUDER)


class PushWithArmy(Order):

    army_selected = False
    push_ordered = False

    def __init__(self, base_location):
        Order.__init__(self, base_location)

    def done(self, observations: Observations):
        return self.push_ordered

    def execute(self, observations: Observations):
        if not self.army_selected:
            if _SELECT_ARMY in observations.available_actions():
                self.army_selected = True
                return actions.FunctionCall(_SELECT_ARMY, [_NOT_QUEUED])
        elif self.army_selected and _ATTACK_MINIMAP in observations.available_actions():
            self.push_ordered = True
            if self.base_location.top_left():
                return actions.FunctionCall(_ATTACK_MINIMAP, [_NOT_QUEUED, [39, 45]])
            return actions.FunctionCall(_ATTACK_MINIMAP, [_NOT_QUEUED, [21, 24]])
        return actions.FunctionCall(_NOOP, [])


class MorphOrbitalCommand(Order):

    command_center_selected = False
    orbital_command_built = False

    def __init__(self, base_location):
        Order.__init__(self, base_location)

    def done(self, observations: Observations):
        return self.orbital_command_built

    def execute(self, observations: Observations):
        if not self.command_center_selected:
            unit_type = observations.screen().unit_type()
            center_y, center_x = (unit_type == _TERRAN_COMMANDCENTER).nonzero()
            center_x = round(center_x.mean())
            center_y = round(center_y.mean())
            target = [center_x, center_y]
            self.command_center_selected = True
            return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])
        elif self.command_center_selected and _MORPH_ORBITAL_COMMAND in observations.available_actions():
            self.orbital_command_built = True
            return actions.FunctionCall(_MORPH_ORBITAL_COMMAND, [_NOT_QUEUED])
        return actions.FunctionCall(_NOOP, [])


class BuildTechLabBarracks(Order):

    barracks_selected = False
    tech_lab_built = False

    def __init__(self, base_location):
        Order.__init__(self, base_location)

    def done(self, observations: Observations):
        return self.tech_lab_built

    def execute(self, observations: Observations):
        if not self.barracks_selected:
            unit_type = observations.screen().unit_type()
            unit_y, unit_x = (unit_type == _TERRAN_BARRACKS).nonzero()
            target = [int(unit_x.mean()), int(unit_y.mean())]
            self.barracks_selected = True
            return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])
        elif _BUILD_TECHLAB_BARRACKS in observations.available_actions():
            self.tech_lab_built = True
            unit_type = observations.screen().unit_type()
            unit_y, unit_x = (unit_type == _TERRAN_BARRACKS).nonzero()
            target = [int(unit_x.mean()), int(unit_y.mean())]
            return actions.FunctionCall(_BUILD_TECHLAB_BARRACKS, [_NOT_QUEUED, target])

        return actions.FunctionCall(_NOOP, [])


class NoOrder(Order):

    def __init__(self, base_location):
        Order.__init__(self, base_location)

    def done(self, observations: Observations):
        return True

    def execute(self, obs: Observations):
        return actions.FunctionCall(_NOOP, [])
