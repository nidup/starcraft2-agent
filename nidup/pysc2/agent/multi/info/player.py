
from nidup.pysc2.wrapper.observations import Observations
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
    def base_location_on_minimap(self):
        center_offset = 16 / 2
        if self.base_top_left:
            left_corner = [15, 9]
        else:
            left_corner = [39, 32]
        return [left_corner[0] + center_offset, left_corner[1] + center_offset]

    def other_unknown_bases_locations_on_minimap(self):
        locations = []
        if self.base_top_left:
            locations.append([45, 45])
        else:
            locations.append([21, 15])
        locations.append([45, 15])
        locations.append([21, 45])
        return locations


class BuildingCounter:

    def command_center_count(self, observations: Observations) -> int:
        unit_type = observations.screen().unit_type()
        unit_type_ids = UnitTypeIds()
        cc_y, cc_x = (unit_type == unit_type_ids.terran_command_center()).nonzero()
        cc_count = 1 if cc_y.any() else 0
        return cc_count

    def supply_depots_count(self, observations: Observations) -> int:
        unit_type = observations.screen().unit_type()
        unit_type_ids = UnitTypeIds()
        depot_y, depot_x = (unit_type == unit_type_ids.terran_supply_depot()).nonzero()
        supply_depot_count = int(round(len(depot_y) / 69))
        return supply_depot_count

    def barracks_count(self, observations: Observations) -> int:
        unit_type = observations.screen().unit_type()
        unit_type_ids = UnitTypeIds()
        barracks_y, barracks_x = (unit_type == unit_type_ids.terran_barracks()).nonzero()
        barracks_count = int(round(len(barracks_y) / 137))
        return barracks_count

    def techlab_barracks_count(self, observations: Observations) -> int:
        unit_type = observations.screen().unit_type()
        unit_type_ids = UnitTypeIds()
        techlabs_y, techlabs_x = (unit_type == unit_type_ids.terran_barracks_techlab()).nonzero()
        if techlabs_y.any():
            return 1
        return 0

    def reactor_barracks_count(self, observations: Observations) -> int:
        unit_type = observations.screen().unit_type()
        unit_type_ids = UnitTypeIds()
        reactor_y, reactor_x = (unit_type == unit_type_ids.terran_barracks_reactor()).nonzero()
        if reactor_y.any():
            return 1
        return 0

    def refineries_count(self, observations: Observations) -> int:
        unit_type = observations.screen().unit_type()
        unit_type_ids = UnitTypeIds()
        unit_y, unit_x = (unit_type == unit_type_ids.terran_refinery()).nonzero()
        units_count = int(round(len(unit_y) / 97))
        return units_count

    def factories_count(self, observations: Observations) -> int:
        unit_type = observations.screen().unit_type()
        unit_type_ids = UnitTypeIds()
        factories_y, factories_x = (unit_type == unit_type_ids.terran_factory()).nonzero()
        factories_count = int(round(len(factories_y) / 137))
        return factories_count

    def starports_count(self, observations: Observations) -> int:
        unit_type = observations.screen().unit_type()
        unit_type_ids = UnitTypeIds()
        starports_y, starports_x = (unit_type == unit_type_ids.terran_starport()).nonzero()
        starports_count = int(round(len(starports_y) / 137))
        return starports_count
