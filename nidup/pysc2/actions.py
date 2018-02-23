
from pysc2.lib import actions

_NOOP = actions.FUNCTIONS.no_op.id
_TERRAN_SCV = 45
_SELECT_POINT = actions.FUNCTIONS.select_point.id
_SELECT_UNIT = actions.FUNCTIONS.select_unit.id
_MOVE_SCREEN = actions.FUNCTIONS.Move_screen.id
_MOVE_MINIMAP = actions.FUNCTIONS.Move_minimap.id
_SELECT_CONTROL_GROUP = actions.FUNCTIONS.select_control_group.id
_SELECT_IDLE_WORKER = actions.FUNCTIONS.select_idle_worker.id
_NOT_QUEUED = [0]
_QUEUED = [1]


class TerranActionIds:

    def no_op(self) -> int:
        return _NOOP

    def move_minimap(self) -> int:
        return _MOVE_MINIMAP


class TerranActions:

    def no_op(self) -> actions.FunctionCall:
        return actions.FunctionCall(_NOOP, [])

    def select_idle_worker(self) -> actions.FunctionCall:
        return actions.FunctionCall(_SELECT_IDLE_WORKER, [_NOT_QUEUED])

    def move_minimap(self, target) -> actions.FunctionCall:
        return actions.FunctionCall(_MOVE_MINIMAP, [_NOT_QUEUED, target])

    def select_point(self, target) -> actions.FunctionCall:
        return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])


