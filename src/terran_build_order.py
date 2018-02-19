
from pysc2.lib import actions
from observations import Observations

# Functions
_BUILD_BARRACKS = actions.FUNCTIONS.Build_Barracks_screen.id
_BUILD_SUPPLYDEPOT = actions.FUNCTIONS.Build_SupplyDepot_screen.id
_NOOP = actions.FUNCTIONS.no_op.id
_SELECT_POINT = actions.FUNCTIONS.select_point.id
_TRAIN_MARINE = actions.FUNCTIONS.Train_Marine_quick.id
_RALLY_UNITS_MINIMAP = actions.FUNCTIONS.Rally_Units_minimap.id
_SELECT_ARMY = actions.FUNCTIONS.select_army.id
_ATTACK_MINIMAP = actions.FUNCTIONS.Attack_minimap.id

# Unit IDs
_TERRAN_BARRACKS = 21
_TERRAN_COMMANDCENTER = 18
_TERRAN_SUPPLYDEPOT = 19
_TERRAN_SCV = 45

# Parameters
_NOT_QUEUED = [0]
_QUEUED = [1]


# cf http://liquipedia.net/starcraft2/MMM_Timing_Push
class MMMTimingPushBuildOrder:

    orders = None
    current_order = None
    current_order_index = None

    def __init__(self, base_top_left):
        base_location = BaseLocation(base_top_left)
        self.orders = [
            BuildSupplyDepot(base_location, 0, 20),
            BuildBarracks(base_location, 20, 0),
            TrainMarine(base_location),
            BuildSupplyDepot(base_location, 20, 20),
            TrainMarine(base_location)
            #NoOrder(base_location)
        ]
        self.current_order_index = 0
        self.current_order = self.orders[0]

    def action(self, observations):
        if self.current_order.done():
            self.next_order()
        return self.current_order.execute(observations)

    def next_order(self):
        self.current_order_index = self.current_order_index + 1
        if self.current_order_index < len(self.orders):
            self.current_order = self.orders[self.current_order_index]
            print("order")
            print(self.current_order)
        else:
            self.current_order = self.orders[len(self.orders) - 1]


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


class Order:
    base_location = None

    def __init__(self, base_location):
        self.base_location = base_location

    def done(self):
        raise NotImplementedError("Should be implemented by concrete order")

    def execute(self, observations: Observations):
        raise NotImplementedError("Should be implemented by concrete order")


class BuildSupplyDepot(Order):

    scv_selected = False
    supply_depot_built = False
    x_from_base = None
    y_from_base = None

    def __init__(self, base_location, x_from_base, y_from_base):
        Order.__init__(self, base_location)
        self.x_from_base = x_from_base
        self.y_from_base = y_from_base

    def done(self):
        return self.supply_depot_built

    def execute(self, observations: Observations):
        if not self.supply_depot_built:
            if not self.scv_selected:
                unit_type = observations.screen().unit_type()
                unit_y, unit_x = (unit_type == _TERRAN_SCV).nonzero()

                target = [unit_x[0], unit_y[0]]

                self.scv_selected = True

                return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])
            elif _BUILD_SUPPLYDEPOT in observations.available_actions():
                unit_type = observations.screen().unit_type()
                unit_y, unit_x = (unit_type == _TERRAN_COMMANDCENTER).nonzero()

                target = self.base_location.transform_location(
                    int(unit_x.mean()),
                    self.x_from_base,
                    int(unit_y.mean()),
                    self.y_from_base
                )

                self.supply_depot_built = True

                return actions.FunctionCall(_BUILD_SUPPLYDEPOT, [_NOT_QUEUED, target])
        return actions.FunctionCall(_NOOP, [])


class BuildBarracks(Order):

    scv_selected = False
    barracks_built = False
    barracks_selected = False
    barracks_rallied = False

    x_from_base = None
    y_from_base = None

    def __init__(self, base_location, x_from_base, y_from_base):
        Order.__init__(self, base_location)
        self.x_from_base = x_from_base
        self.y_from_base = y_from_base

    def done(self):
        return self.barracks_rallied

    def execute(self, observations: Observations):
        if not self.barracks_built:
            if _BUILD_BARRACKS in observations.available_actions():
                unit_type = observations.screen().unit_type()
                unit_y, unit_x = (unit_type == _TERRAN_COMMANDCENTER).nonzero()

                target = self.base_location.transform_location(
                    int(unit_x.mean()),
                    self.x_from_base,
                    int(unit_y.mean()),
                    self.y_from_base
                )

                self.barracks_built = True

                return actions.FunctionCall(_BUILD_BARRACKS, [_NOT_QUEUED, target])
            elif not self.scv_selected:
                unit_type = observations.screen().unit_type()
                unit_y, unit_x = (unit_type == _TERRAN_SCV).nonzero()

                target = [unit_x[0], unit_y[0]]

                self.scv_selected = True

                return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])
        elif not self.barracks_rallied:
            if not self.barracks_selected:
                unit_type = observations.screen().unit_type()
                unit_y, unit_x = (unit_type == _TERRAN_BARRACKS).nonzero()

                if unit_y.any():
                    target = [int(unit_x.mean()), int(unit_y.mean())]

                    self.barracks_selected = True

                    return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])
            else:
                self.barracks_rallied = True

                if self.base_location.top_left():
                    return actions.FunctionCall(_RALLY_UNITS_MINIMAP, [_NOT_QUEUED, [29, 21]])

                return actions.FunctionCall(_RALLY_UNITS_MINIMAP, [_NOT_QUEUED, [29, 46]])
        return actions.FunctionCall(_NOOP, [])


class TrainMarine(Order):

    barracks_selected = False
    army_selected = False
    army_rallied = False
    done = False

    def __init__(self, base_location):
        Order.__init__(self, base_location)

    def done(self):
        return self.army_rallied

    def execute(self, observations: Observations):
        if observations.player().food_used() < observations.player().food_cap() and _TRAIN_MARINE in observations.available_actions():
            return actions.FunctionCall(_TRAIN_MARINE, [_QUEUED])
        elif not self.barracks_selected:
            unit_type = observations.screen().unit_type()
            unit_y, unit_x = (unit_type == _TERRAN_BARRACKS).nonzero()
            if unit_y.any():
                target = [int(unit_x.mean()), int(unit_y.mean())]
                self.barracks_selected = True
            return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])
        elif not self.army_rallied:
            if not self.army_selected:
                if _SELECT_ARMY in observations.available_actions():
                    self.army_selected = True
                    self.barracks_selected = False
                    return actions.FunctionCall(_SELECT_ARMY, [_NOT_QUEUED])
            elif _ATTACK_MINIMAP in observations.available_actions():
                self.army_rallied = True
                self.army_selected = False
                if self.base_location.top_left():
                    return actions.FunctionCall(_ATTACK_MINIMAP, [_NOT_QUEUED, [39, 45]])
                return actions.FunctionCall(_ATTACK_MINIMAP, [_NOT_QUEUED, [21, 24]])
        return actions.FunctionCall(_NOOP, [])


class NoOrder(Order):

    def __init__(self, base_location):
        Order.__init__(self, base_location)

    def done(self):
        return True

    def execute(self, obs: Observations):
        return actions.FunctionCall(_NOOP, [])
