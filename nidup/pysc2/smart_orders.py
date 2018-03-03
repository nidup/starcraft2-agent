
import random
import math
from pysc2.lib import actions
from nidup.pysc2.actions import TerranActions, TerranActionIds
from nidup.pysc2.observations import Observations
from nidup.pysc2.unit_types import UnitTypeIds

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

    def top_left(self):
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


class SmartOrder:
    def __init__(self, location: Location):
        self.location = location
        self.actions = TerranActions()
        self.action_ids = TerranActionIds()
        self.unit_type_ids = UnitTypeIds()


class BuildBarracks(SmartOrder):

    def select_scv(self, observations: Observations) -> actions.FunctionCall:
        unit_type = observations.screen().unit_type()
        unit_y, unit_x = (unit_type == self.unit_type_ids.terran_scv()).nonzero()
        if unit_y.any():
            i = random.randint(0, len(unit_y) - 1)
            target = [unit_x[i], unit_y[i]]
            return self.actions.select_point(target)

        return self.actions.no_op()

    def build(self, observations: Observations) -> actions.FunctionCall:
        unit_type = observations.screen().unit_type()
        cc_x, cc_y = self.location.command_center_position()
        barracks_y, barracks_x = (unit_type == self.unit_type_ids.terran_barracks()).nonzero()
        barracks_count = int(round(len(barracks_y) / 137))
        if barracks_count < 2 and self.action_ids.build_barracks() in observations.available_actions():
            if cc_y.any():
                if barracks_count == 0:
                    target = self.location.transform_distance(round(cc_x.mean()), 15, round(cc_y.mean()), -9)
                elif barracks_count == 1:
                    target = self.location.transform_distance(round(cc_x.mean()), 15, round(cc_y.mean()), 12)
                return self.actions.build_barracks(target)
        return self.actions.no_op()


class BuildSupplyDepot(SmartOrder):

    def select_scv(self, observations: Observations) -> actions.FunctionCall:
        unit_type = observations.screen().unit_type()
        unit_y, unit_x = (unit_type == self.unit_type_ids.terran_scv()).nonzero()
        if unit_y.any():
            i = random.randint(0, len(unit_y) - 1)
            target = [unit_x[i], unit_y[i]]
            return self.actions.select_point(target)
        return self.actions.no_op()

    def build(self, observations: Observations) -> actions.FunctionCall:
        unit_type = observations.screen().unit_type()
        cc_x, cc_y = self.location.command_center_position()
        depot_y, depot_x = (unit_type == self.unit_type_ids.terran_supply_depot()).nonzero()
        supply_depot_count = int(round(len(depot_y) / 69))
        if supply_depot_count < 2 and self.action_ids.build_supply_depot() in observations.available_actions():
            if cc_y.any():
                if supply_depot_count == 0:
                    target = self.location.transform_distance(round(cc_x.mean()), -35, round(cc_y.mean()), 0)
                elif supply_depot_count == 1:
                    target = self.location.transform_distance(round(cc_x.mean()), -25, round(cc_y.mean()), -25)
                return self.actions.build_supply_depot(target)
        return self.actions.no_op()


class BuildMarine(SmartOrder):

    def select_barracks(self, observations: Observations) -> actions.FunctionCall:
        unit_type = observations.screen().unit_type()
        barracks_y, barracks_x = (unit_type == self.unit_type_ids.terran_barracks()).nonzero()
        if barracks_y.any():
            i = random.randint(0, len(barracks_y) - 1)
            target = [barracks_x[i], barracks_y[i]]
            return self.actions.select_point_all(target)
        return self.actions.no_op()

    def train_marine(self, observations: Observations) -> actions.FunctionCall:
        if self.action_ids.train_marine() in observations.available_actions():
            return self.actions.train_marine()
        return self.actions.no_op()


class Attack(SmartOrder):

    def select_army(self, observations: Observations) -> actions.FunctionCall:
        if self.action_ids.select_army() in observations.available_actions():
            return self.actions.select_army()

        return self.actions.no_op()

    def attack_minimap(self, observations: Observations, x, y) -> actions.FunctionCall:
        do_it = True
        if len(observations.single_select()) > 0 and observations.single_select()[0][0] == self.unit_type_ids.terran_scv():
            do_it = False

        if len(observations.multi_select()) > 0 and observations.multi_select()[0][0] == self.unit_type_ids.terran_scv():
            do_it = False

        if do_it and self.action_ids.attack_minimap() in observations.available_actions():
            x_offset = random.randint(-1, 1)
            y_offset = random.randint(-1, 1)
            target = self.location.transform_location(int(x) + (x_offset * 8), int(y) + (y_offset * 8))
            return self.actions.attack_minimap(target)

        return self.actions.no_op()
