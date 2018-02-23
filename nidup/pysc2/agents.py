from pysc2.agents.base_agent import BaseAgent
from nidup.pysc2.terran_build_order import MMMTimingPushBuildOrder, BaseLocation
from nidup.pysc2.observations import Observations
import time

from sklearn.cluster import KMeans
import math
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


class BuildOrderAgent(BaseAgent):

    build_order = None
    debug = False

    def step(self, obs):
        super(BuildOrderAgent, self).step(obs)
        observations = Observations(obs)
        if self.build_order is None:
            base_location = BaseLocation(observations)
            self.build_order = MMMTimingPushBuildOrder(base_location)
        if self.debug:
            time.sleep(0.5)
        return self.build_order.action(observations)


class ScoutingAgent(BaseAgent):

    started = False
    base_location = None
    other_bases_minimap_locations = None
    scv_selected = False
    scv_moved = False
    infinite_scouting = True

    def step(self, obs):
        super(ScoutingAgent, self).step(obs)
        observations = Observations(obs)
        if not self.started:
            self.base_location = BaseLocation(observations)
            self.other_bases_minimap_locations = self.base_location.other_unknown_bases_locations_on_minimap()
            self.started = True
        elif not self.scv_selected:
            print("select scv")
            unit_type = observations.screen().unit_type()
            unit_y, unit_x = (unit_type == _TERRAN_SCV).nonzero()
            target = [unit_x[0], unit_y[0]]
            self.scv_selected = True
            return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])
        elif not self.scv_moved and _MOVE_MINIMAP in observations.available_actions():
            print("scv is scouting")
            unit_y, unit_x = self.other_bases_minimap_locations.pop(0)
            target = [unit_x, unit_y]
            self.scv_moved = True
            return actions.FunctionCall(_MOVE_MINIMAP, [_NOT_QUEUED, target])
        elif self.scv_moved and observations.player().idle_worker_count() > 0 and len(self.other_bases_minimap_locations) > 0:
            print("select idle scv")
            self.scv_moved = False
            return actions.FunctionCall(_SELECT_IDLE_WORKER, [_NOT_QUEUED])
        elif self.infinite_scouting and len(self.other_bases_minimap_locations) == 0:
            self.other_bases_minimap_locations = self.base_location.other_unknown_bases_locations_on_minimap()
        return actions.FunctionCall(_NOOP, [])
