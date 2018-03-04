

from nidup.pysc2.observations import Observations, ScreenFeatures
from nidup.pysc2.wrapper.unit_types import UnitTypeIds

# Parameters
_PLAYER_SELF = 1


class BaseLocation:

    base_top_left = None
    unit_type_ids = None

    def __init__(self, observations: Observations):
        player_y, player_x = (observations.minimap().player_relative() == _PLAYER_SELF).nonzero()
        self.base_top_left = player_y.mean() <= 31
        self.unit_type_ids = UnitTypeIds()

    def top_left(self):
        return self.base_top_left

    # TODO,
    # handle ValueError: Argument is out of range for 91/Build_SupplyDepot_screen (3/queued [2]; 0/screen [0, 0]), got: [[0], [66, -1]]
    # should never return negative position
    def transform_location(self, x, x_distance, y, y_distance):
        if not self.base_top_left:
            return [x - x_distance, y - y_distance]

        return [x + x_distance, y + y_distance]

    def locate_command_center(self, screen: ScreenFeatures):
        unit_type = screen.unit_type()
        unit_y, unit_x = (unit_type == self.unit_type_ids.terran_command_center()).nonzero()
        if not unit_x.any():
            unit_y, unit_x = (unit_type == self.unit_type_ids.terran_orbital_command()).nonzero()
        return unit_y, unit_x

    def camera_centered_on_command_center(self, screen: ScreenFeatures) -> bool:
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


class StepIndex:

    step_index = 0

    def increment_step(self):
        self.step_index = self.step_index + 1

    def __str__(self) -> str:
        return "step index :" + self.step_index.__str__()
