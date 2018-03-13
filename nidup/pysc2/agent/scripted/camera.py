
from pysc2.lib import actions
from nidup.pysc2.agent.order import Order
from nidup.pysc2.wrapper.actions import TerranActions
from nidup.pysc2.wrapper.observations import Observations


class CenterCameraOnCommandCenter(Order):

    def __init__(self, base_location):
        Order.__init__(self)
        self.base_location = base_location
        self.actions = TerranActions()
        self.centered_on_base = False

    def done(self, observations: Observations) -> bool:
        return self.centered_on_base

    def execute(self, observations: Observations) -> actions.FunctionCall:
        if not self.centered_on_base:
            unit_y, unit_x = self.base_location.base_location_on_minimap()
            target = [unit_x, unit_y]
            self.centered_on_base = True
            return self.actions.move_camera(target)
        return self.actions.no_op()


class MoveCameraOnMinimapTarget(Order):

    def __init__(self, base_location, minimap_target_x: int, minimap_target_y: int):
        Order.__init__(self)
        self.base_location = base_location
        self.actions = TerranActions()
        self.camera_moved = False
        self.minimap_target_x = minimap_target_x
        self.minimap_target_y = minimap_target_y

    def done(self, observations: Observations) -> bool:
        return self.camera_moved

    def execute(self, observations: Observations) -> actions.FunctionCall:
        if not self.camera_moved:
            target = [self.minimap_target_x, self.minimap_target_y]
            self.camera_moved = True
            return self.actions.move_camera(target)
        return self.actions.no_op()
