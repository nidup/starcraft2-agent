
from nidup.pysc2.wrapper.observations import Observations, ScreenFeatures
from nidup.pysc2.wrapper.unit_types import UnitTypeIds

# Parameters
_PLAYER_SELF = 1


class Location:

    def __init__(self, first_observations: Observations):
        player_y, player_x = (first_observations.minimap().player_relative() == _PLAYER_SELF).nonzero()
        self.base_top_left = player_y.mean() <= 31
        unit_type = first_observations.screen().unit_type()
        self.unit_type_ids = UnitTypeIds()
        self.cc_y, self.cc_x = (unit_type == self.unit_type_ids.terran_command_center()).nonzero()

    def command_center_is_top_left(self) -> bool:
        return self.base_top_left

    def command_center_first_position(self):
        return self.cc_x, self.cc_y

    # handle ValueError: Argument is out of range for 91/Build_SupplyDepot_screen (3/queued [2]; 0/screen [0, 0]), got: [[0], [66, -1]]
    # should never return negative position
    def transform_distance(self, x, x_distance, y, y_distance):
        if not self.base_top_left:
            return [x - x_distance, y - y_distance]

        return [x + x_distance, y + y_distance]

    def transform_location(self, x, y):
        if not self.base_top_left:
            return [64 - x, 64 - y]

        return [x, y]

    def locate_command_center(self, screen: ScreenFeatures):
        unit_type = screen.unit_type()
        unit_y, unit_x = (unit_type == self.unit_type_ids.terran_command_center()).nonzero()
        if not unit_x.any():
            unit_y, unit_x = (unit_type == self.unit_type_ids.terran_orbital_command()).nonzero()
        return unit_y, unit_x

    def command_center_is_visible(self, screen: ScreenFeatures) -> bool:
        unit_y, unit_x = self.locate_command_center(screen)
        if unit_y.any():
            return True
        else:
            return False

    def base_location_on_minimap(self):
        if self.base_top_left:
            return [21, 15]
        else:
            return [45, 45]

    def other_unknown_bases_locations_on_minimap(self):
        locations = []
        if self.base_top_left:
            locations.append([45, 45])
        else:
            locations.append([21, 15])
        locations.append([45, 15])
        locations.append([21, 45])
        return locations
