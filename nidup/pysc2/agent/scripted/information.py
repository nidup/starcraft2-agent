
from nidup.pysc2.wrapper.observations import Observations, ScreenFeatures, MinimapFeatures
from nidup.pysc2.wrapper.unit_types import UnitTypeIds

# Parameters
_PLAYER_SELF = 1
_PLAYER_ENEMY = 4

class Location:

    def __init__(self, first_observations: Observations):
        player_y, player_x = (first_observations.minimap().player_relative() == _PLAYER_SELF).nonzero()
        self.base_top_left = player_y.mean() <= 31
        unit_type = first_observations.screen().unit_type()
        self.unit_type_ids = UnitTypeIds()
        self.cc_y, self.cc_x = (unit_type == self.unit_type_ids.terran_command_center()).nonzero()

    def command_center_is_top_left(self) -> bool:
        return self.base_top_left

    # return [y, x]
    def command_center_first_position(self):
        return self.cc_y, self.cc_x

    # handle ValueError: Argument is out of range for 91/Build_SupplyDepot_screen (3/queued [2]; 0/screen [0, 0]), got: [[0], [66, -1]]
    # should never return negative position
    # ValueError: Argument is out of range for 42/Build_Barracks_screen (3/queued [2]; 0/screen [0, 0]), got: [[0], [10, -4]]
    def transform_distance(self, x, x_distance, y, y_distance):
        if not self.base_top_left:
            return [x - x_distance, y - y_distance]

        return [x + x_distance, y + y_distance]

    def transform_location(self, x, y):
        if not self.base_top_left:
            return [64 - x, 64 - y]

        return [x, y]

    # return [y, x]
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

    # return [y, x]
    def base_location_on_minimap(self):
        center_offset = 16 / 2
        if self.base_top_left:
            left_corner = [15, 9]
        else:
            left_corner = [39, 32]
        return [left_corner[0] + center_offset, left_corner[1] + center_offset]

    # return [y, x]
    def current_visible_minimap_left_corner(self, minimap: MinimapFeatures):
        camera_x = None
        camera_y = None
        for ind_column, column in enumerate(minimap.camera()):
            for ind_line, cell in enumerate(column):
                if cell == 1 and not camera_x:
                    camera_x = ind_line
                    camera_y = ind_column
        return camera_y, camera_x

    def other_unknown_bases_locations_on_minimap(self):
        locations = []
        if self.base_top_left:
            locations.append([45, 45])
        else:
            locations.append([21, 15])
        locations.append([45, 15])
        locations.append([21, 45])
        return locations
