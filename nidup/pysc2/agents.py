
from pysc2.agents.base_agent import BaseAgent
from nidup.pysc2.commanders import GameCommander, ScoutingCommander
from nidup.pysc2.observations import Observations
from nidup.pysc2.information import BaseLocation
import time

from nidup.pysc2.actions import TerranActions, TerranActionIds
from nidup.pysc2.unit_types import UnitTypeIds


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

    commander = None
    infinite_scouting = True

    def step(self, obs):
        super(ScoutingAgent, self).step(obs)
        observations = Observations(obs)
        if self.commander is None:
            base_location = BaseLocation(observations)
            self.commander = ScoutingCommander(base_location, self.infinite_scouting)
        return self.commander.order(observations).execute(observations)


class ControlGroupsAgent(BaseAgent):

    base_location = None
    actions = None
    action_ids = None
    unit_type_ids = None
    started = False
    scv_selected = False
    scv_grouped = False
    scv_moved = False
    second_scv_selected = False
    second_scv_grouped = False
    second_scv_moved = False
    group_one_selected = False

    def __init__(self):
        BaseAgent.__init__(self)
        self.actions = TerranActions()
        self.action_ids = TerranActionIds()
        self.unit_type_ids = UnitTypeIds()

    def step(self, obs):
        super(ControlGroupsAgent, self).step(obs)
        observations = Observations(obs)
        if not self.started:
            self.base_location = BaseLocation(observations)
            self.started = True
        elif not self.scv_selected:
            unit_type = observations.screen().unit_type()
            unit_y, unit_x = (unit_type == self.unit_type_ids.terran_scv()).nonzero()
            target = [unit_x[0], unit_y[0]]
            self.scv_selected = True
            return self.actions.select_point(target)
        elif not self.scv_grouped:
            self.scv_grouped = True
            return self.actions.set_control_group(1)
        elif not self.scv_moved:
            self.scv_moved = True
            unit_y, unit_x = self.base_location.other_unknown_bases_locations_on_minimap().pop(1)
            target = [unit_x, unit_y]
            return self.actions.move_minimap(target)
        elif not self.second_scv_selected:
            unit_type = observations.screen().unit_type()
            unit_y, unit_x = (unit_type == self.unit_type_ids.terran_scv()).nonzero()
            target = [unit_x[1], unit_y[1]]
            self.second_scv_selected = True
            return self.actions.select_point(target)
        elif not self.second_scv_grouped:
            self.second_scv_grouped = True
            return self.actions.add_control_group(1)
        elif not self.second_scv_moved:
           self.second_scv_moved = True
           unit_y, unit_x = self.base_location.other_unknown_bases_locations_on_minimap().pop(2)
           target = [unit_x, unit_y]
           return self.actions.move_minimap(target)
        elif not self.group_one_selected:
           self.group_one_selected = True
           return self.actions.select_control_group(1)

        #print(observations.control_groups())

        return self.actions.no_op()
