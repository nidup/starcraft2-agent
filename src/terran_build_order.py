
from pysc2.lib import actions
from pysc2.lib import features

# Functions
_BUILD_BARRACKS = actions.FUNCTIONS.Build_Barracks_screen.id
_BUILD_SUPPLYDEPOT = actions.FUNCTIONS.Build_SupplyDepot_screen.id
_NOOP = actions.FUNCTIONS.no_op.id
_SELECT_POINT = actions.FUNCTIONS.select_point.id
_TRAIN_MARINE = actions.FUNCTIONS.Train_Marine_quick.id
_RALLY_UNITS_MINIMAP = actions.FUNCTIONS.Rally_Units_minimap.id
_SELECT_ARMY = actions.FUNCTIONS.select_army.id
_ATTACK_MINIMAP = actions.FUNCTIONS.Attack_minimap.id

# Features
_UNIT_TYPE = features.SCREEN_FEATURES.unit_type.index

# Unit IDs
_TERRAN_BARRACKS = 21
_TERRAN_COMMANDCENTER = 18
_TERRAN_SUPPLYDEPOT = 19
_TERRAN_SCV = 45

# Parameters
_SUPPLY_USED = 3
_SUPPLY_MAX = 4
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
            BuildSupplyDepot(base_location),
            BuildBarracks(base_location),
            TrainMarine(base_location),
            NoOrder(base_location)
        ]
        self.current_order_index = 0
        self.current_order = self.orders[0]

    def action(self, obs):

        if self.current_order.done():
            self.next_order()

        return self.current_order.execute(obs)

    def next_order(self):
        self.current_order_index = self.current_order_index + 1
        if self.current_order_index < len(self.orders):
            self.current_order = self.orders[self.current_order_index]
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
        raise NotImplementedError( "Should be implemented by concrete order" )

    def execute(self, obs):
        raise NotImplementedError( "Should be implemented by concrete order" )


class BuildSupplyDepot(Order):

    scv_selected = False
    supply_depot_built = False

    def __init__(self, base_location):
        Order.__init__(self, base_location)

    def done(self):
        return self.supply_depot_built

    def execute(self, obs):
        if not self.supply_depot_built:
            if not self.scv_selected:
                unit_type = obs.observation["screen"][_UNIT_TYPE]
                unit_y, unit_x = (unit_type == _TERRAN_SCV).nonzero()

                target = [unit_x[0], unit_y[0]]

                self.scv_selected = True

                return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])
            elif _BUILD_SUPPLYDEPOT in obs.observation["available_actions"]:
                unit_type = obs.observation["screen"][_UNIT_TYPE]
                unit_y, unit_x = (unit_type == _TERRAN_COMMANDCENTER).nonzero()

                target = self.base_location.transform_location(int(unit_x.mean()), 0, int(unit_y.mean()), 20)

                self.supply_depot_built = True

                return actions.FunctionCall(_BUILD_SUPPLYDEPOT, [_NOT_QUEUED, target])
        return actions.FunctionCall(_NOOP, [])

class BuildBarracks(Order):

    barracks_built = False
    barracks_selected = False
    barracks_rallied = False
    # TODO select vcs

    def __init__(self, base_location):
        Order.__init__(self, base_location)

    def done(self):
        return self.barracks_rallied

    def execute(self, obs):
        if not self.barracks_built:
            if _BUILD_BARRACKS in obs.observation["available_actions"]:
                unit_type = obs.observation["screen"][_UNIT_TYPE]
                unit_y, unit_x = (unit_type == _TERRAN_COMMANDCENTER).nonzero()

                target = self.base_location.transform_location(int(unit_x.mean()), 20, int(unit_y.mean()), 0)

                self.barracks_built = True

                return actions.FunctionCall(_BUILD_BARRACKS, [_NOT_QUEUED, target])
        elif not self.barracks_rallied:
            if not self.barracks_selected:
                unit_type = obs.observation["screen"][_UNIT_TYPE]
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

    def __init__(self, base_location):
        Order.__init__(self, base_location)

    def done(self):
        return self.army_rallied

    def execute(self, obs):
        if obs.observation["player"][_SUPPLY_USED] < obs.observation["player"][_SUPPLY_MAX] and _TRAIN_MARINE in obs.observation["available_actions"]:
            return actions.FunctionCall(_TRAIN_MARINE, [_QUEUED])
        elif not self.army_rallied:
            if not self.army_selected:
                if _SELECT_ARMY in obs.observation["available_actions"]:
                    self.army_selected = True
                    self.barracks_selected = False

                    return actions.FunctionCall(_SELECT_ARMY, [_NOT_QUEUED])
            elif _ATTACK_MINIMAP in obs.observation["available_actions"]:
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

    def execute(self, obs):
        return actions.FunctionCall(_NOOP, [])
