from pysc2.agents.base_agent import BaseAgent
from nidup.pysc2.commanders import GameCommander
from nidup.pysc2.observations import Observations
from nidup.pysc2.information import BaseLocation
from nidup.pysc2.actions import TerranActions, TerranActionIds
from nidup.pysc2.unit_types import UnitTypeIds
import time


class BuildOrderAgent(BaseAgent):

    commander = None
    debug = False

    def step(self, obs):
        super(BuildOrderAgent, self).step(obs)
        observations = Observations(obs)
        if self.commander is None:
            base_location = BaseLocation(observations)
            self.commander = GameCommander(base_location)
        if self.debug:
            time.sleep(0.5)
        return self.commander.order(observations).execute(observations)


class ScoutingAgent(BaseAgent):

    actions: None
    action_ids: None
    unit_type_ids: None
    started = False
    base_location = None
    other_bases_minimap_locations = None
    scv_selected = False
    scv_moved = False
    infinite_scouting = True

    def __init__(self):
        BaseAgent.__init__(self)
        self.actions = TerranActions()
        self.action_ids = TerranActionIds()
        self.unit_type_ids = UnitTypeIds()

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
            unit_y, unit_x = (unit_type == self.unit_type_ids.terran_scv()).nonzero()
            target = [unit_x[0], unit_y[0]]
            self.scv_selected = True
            return self.actions.select_point(target)
        elif not self.scv_moved and self.action_ids.move_minimap() in observations.available_actions():
            print("scv is scouting")
            unit_y, unit_x = self.other_bases_minimap_locations.pop(0)
            target = [unit_x, unit_y]
            self.scv_moved = True
            return self.actions.move_minimap(target)
        elif self.scv_moved and observations.player().idle_worker_count() > 0 and len(self.other_bases_minimap_locations) > 0:
            print("select idle scv")
            self.scv_moved = False
            return self.actions.select_idle_worker()
        elif self.infinite_scouting and len(self.other_bases_minimap_locations) == 0:
            self.other_bases_minimap_locations = self.base_location.other_unknown_bases_locations_on_minimap()
        return self.actions.no_op()
