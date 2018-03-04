
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.wrapper.unit_types import UnitTypeIds

# Parameters
_PLAYER_SELF = 1


class Location:

    base_top_left = None
    unit_type_ids = None

    def __init__(self, observations: Observations):
        player_y, player_x = (observations.minimap().player_relative() == _PLAYER_SELF).nonzero()
        self.base_top_left = player_y.mean() <= 31
        unit_type = observations.screen().unit_type()
        self.cc_y, self.cc_x = (unit_type == UnitTypeIds().terran_command_center()).nonzero()

    def command_center_is_top_left(self) -> bool:
        return self.base_top_left

    def command_center_position(self):
        return self.cc_x, self.cc_y

    def transform_distance(self, x, x_distance, y, y_distance):
        if not self.base_top_left:
            return [x - x_distance, y - y_distance]

        return [x + x_distance, y + y_distance]

    def transform_location(self, x, y):
        if not self.base_top_left:
            return [64 - x, 64 - y]

        return [x, y]
