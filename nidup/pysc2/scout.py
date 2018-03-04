
from pysc2.lib import actions
from nidup.pysc2.wrapper.actions import TerranActions, TerranActionIds
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.order import Order
from nidup.pysc2.information import BaseLocation
from nidup.pysc2.wrapper.unit_types import UnitTypeIds
import random


class Scouting(Order):

    actions: None
    action_ids: None
    unit_type_ids: None
    base_location = None
    other_bases_minimap_locations = None
    scv_selected = False
    scv_moved = False
    scv_back_to_base = False
    infinite_scouting = False

    def __init__(self, base_location: BaseLocation, looping: bool = False):
        Order.__init__(self)
        self.base_location = base_location
        self.other_bases_minimap_locations = self.base_location.other_unknown_bases_locations_on_minimap()
        self.actions = TerranActions()
        self.action_ids = TerranActionIds()
        self.unit_type_ids = UnitTypeIds()
        self.infinite_scouting = looping

    def done(self, observations: Observations) -> bool:
        return self.scv_back_to_base and not self.infinite_scouting

    def execute(self, observations: Observations) -> actions.FunctionCall:
        if not self.scv_selected:
            unit_type = observations.screen().unit_type()
            unit_y, unit_x = (unit_type == self.unit_type_ids.terran_scv()).nonzero()
            rand_unit_index = random.randint(0, len(unit_y) - 1)
            target = [unit_x[rand_unit_index], unit_y[rand_unit_index]]
            self.scv_selected = True
            return self.actions.select_point(target)
        elif not self.scv_moved and self.action_ids.move_minimap() in observations.available_actions():
            unit_y, unit_x = self.other_bases_minimap_locations.pop(0)
            target = [unit_x, unit_y]
            self.scv_moved = True
            return self.actions.move_minimap(target)
        elif self.scv_moved and observations.player().idle_worker_count() > 0 and len(self.other_bases_minimap_locations) > 0:
            self.scv_moved = False
            return self.actions.select_idle_worker()
        elif self.infinite_scouting and len(self.other_bases_minimap_locations) == 0:
            self.other_bases_minimap_locations = self.base_location.other_unknown_bases_locations_on_minimap()
        elif not self.scv_back_to_base and len(self.other_bases_minimap_locations) == 0:
            unit_y, unit_x = self.base_location.base_location_on_minimap()
            target = [unit_x, unit_y]
            self.scv_back_to_base = True
            return self.actions.move_minimap(target)
        return self.actions.no_op()
