
import random
import time
from pysc2.agents.base_agent import BaseAgent
from nidup.pysc2.agent.scripted.commander import GameCommander, ScoutingCommander, NoOrder
from nidup.pysc2.agent.information import Location
from nidup.pysc2.wrapper.actions import TerranActions, TerranActionIds
from nidup.pysc2.wrapper.unit_types import UnitTypeIds
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.learning.game_results import GameResultsTable
from nidup.pysc2.agent.scripted.build import BuildRefinery


class BuildOrderAgent(BaseAgent):

    commander = None
    debug = False

    def step(self, obs):
        super(BuildOrderAgent, self).step(obs)
        observations = Observations(obs)
        if observations.first():
            base_location = Location(observations)
            self.commander = GameCommander(base_location)
        elif observations.last():
            game_results = GameResultsTable(self.name())
            game_results.append(observations.reward(), observations.score_cumulative())
        if self.debug:
            time.sleep(0.5)
        return self.commander.order(observations).execute(observations)

    def name(self) -> str:
        return __name__ + "." + self.__class__.__name__


class ScoutingAgent(BaseAgent):

    commander = None
    infinite_scouting = True

    def step(self, obs):
        super(ScoutingAgent, self).step(obs)
        observations = Observations(obs)
        if observations.first():
            base_location = Location(observations)
            self.commander = ScoutingCommander(base_location, self.infinite_scouting)
        return self.commander.order(observations).execute(observations)


class RefineryAgent(BaseAgent):

    def __init__(self):
        BaseAgent.__init__(self)
        self.actions = TerranActions()
        self.action_ids = TerranActionIds()
        self.unit_type_ids = UnitTypeIds()
        self.base_location = None
        self.order_first_refinery = None
        self.order_second_refinery = None

    def step(self, obs):
        super(RefineryAgent, self).step(obs)
        observations = Observations(obs)
        if observations.first():
            self.base_location = Location(observations)
            self.order_first_refinery = BuildRefinery(self.base_location)
            self.order_second_refinery = BuildRefinery(self.base_location)
        if not self.order_first_refinery.done(observations):
            return self.order_first_refinery.execute(observations)
        elif not self.order_second_refinery.done(observations):
            return self.order_second_refinery.execute(observations)
        return NoOrder().execute(observations)


class ControlGroupsAgent(BaseAgent):

    base_location = None
    actions = None
    action_ids = None
    unit_type_ids = None
    #all_scv_selected = False
    #unit_selected = False
    scv_selected = False
    scv_grouped = False
    scv_moved = False
    second_scv_selected = False
    second_scv_grouped = False
    second_scv_moved = False
    group_one_selected = False
    both_scv_moved = False

    def __init__(self):
        BaseAgent.__init__(self)
        self.actions = TerranActions()
        self.action_ids = TerranActionIds()
        self.unit_type_ids = UnitTypeIds()

    def step(self, obs):
        super(ControlGroupsAgent, self).step(obs)
        observations = Observations(obs)

        #print(observations.available_actions())
        #print(observations.multi_select())
        #print(observations.single_select())
        #print(obs.observation.keys())

        if observations.first():
            self.base_location = Location(observations)
        #if not self.all_scv_selected:
        #    self.all_scv_selected = True
        #   return self.actions.select_rect([0, 0], [83, 83])
        #elif not self.unit_selected:
        #   self.unit_selected = True
        #   return self.actions.select_all_units(0)
        if not self.scv_selected:
            unit_type = observations.screen().unit_type()
            unit_y, unit_x = (unit_type == self.unit_type_ids.terran_scv()).nonzero()
            rand_unit_index = random.randint(0, len(unit_y) - 1)
            target = [unit_x[rand_unit_index], unit_y[rand_unit_index]]
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
            rand_unit_index = random.randint(0, len(unit_y) - 1)
            target = [unit_x[rand_unit_index], unit_y[rand_unit_index]]
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
        elif not self.both_scv_moved:
           self.both_scv_moved = True
           unit_y, unit_x = [32, 32]
           target = [unit_x, unit_y]
           return self.actions.move_minimap(target)

        #print(observations.control_groups())
        #print(observations.screen().selected())
        #return self.actions.no_op()

        return self.actions.no_op()
