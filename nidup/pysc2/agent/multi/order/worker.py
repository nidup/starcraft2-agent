
from pysc2.lib import actions
from nidup.pysc2.agent.information import Location, BuildingCounter
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.agent.multi.order.common import SmartOrder, SCVControlGroups, SCVCommonActions, BuildingPositionsFromCommandCenter


# Groups all scv to specialized group to facilitate the further selections of dedicated workers, at the end of this
# order, control groups look like the following
# print(observations.control_groups())
# [[45 12] <- all scv
#  [45  5] <- mineral scv
#  [45  3] <- vespene1 scv
#  [45  3] <- vespene2 scv
#  [45  1] <- scout scv
#  [0  0]  <- free control group
#  [0  0]
#  [0  0]
#  [0  0]
#  [0  0]]
class PrepareSCVControlGroupsOrder(SmartOrder):

    def __init__(self, location: Location):
        SmartOrder.__init__(self, location)
        self.step = 1
        groups = SCVControlGroups()
        self.all_scv_group_id = groups.all_group_id()
        self.mineral_group_id = groups.mineral_collectors_group_id()
        self.vespene_group1_id = groups.refinery_one_collectors_group_id()
        self.vespene_group2_id = groups.refinery_two_collectors_group_id()
        self.scouting_group_id = groups.scouting_group_id()
        self.expected_group_sizes = {
            self.mineral_group_id: 5,
            self.vespene_group1_id: 3,
            self.vespene_group2_id: 3,
            self.scouting_group_id: 1,
        }
        self.scv_index_in_all_group = 0
        self.current_group_index = 1

    def doable(self, observations: Observations) -> bool:
        return True

    def done(self, observations: Observations) -> bool:
        return self.step == 6

    def execute(self, observations: Observations) -> actions.FunctionCall:
        if self.step == 1:
            return self._select_all_vcs()
        elif self.step == 2:
            return self._add_selected_vcs_to_the_all_group()
        # we loop on the following 3 actions to prepare all specialized groups
        elif self.step == 3:
            return self._select_the_all_group()
        elif self.step == 4:
            return self._select_a_new_vcs_from_all_group(observations)
        elif self.step == 5:
            return self._add_selected_vcs_to_a_specialized_group(self.current_group_index)
        return self.actions.no_op()

    def _select_all_vcs(self) -> actions.FunctionCall:
        self.step = self.step + 1
        return self.actions.select_rect([0, 0], [83, 83])

    def _add_selected_vcs_to_the_all_group(self) -> actions.FunctionCall:
        self.step = self.step + 1
        return self.actions.add_control_group(self.all_scv_group_id)

    def _select_the_all_group(self) -> actions.FunctionCall:
        self.step = self.step + 1
        return self.actions.select_control_group(self.all_scv_group_id)

    def _select_a_new_vcs_from_all_group(self, observations: Observations) -> actions.FunctionCall:
        if self.action_ids.select_unit() in observations.available_actions():
            self.step = self.step + 1
            action = self.actions.select_unit(self.scv_index_in_all_group)
            self.scv_index_in_all_group = self.scv_index_in_all_group + 1
            return action

    def _add_selected_vcs_to_a_specialized_group(self, group_id: int) -> actions.FunctionCall:
        self.step = self.step + 1
        self._goto_next_vcs_to_group(group_id)
        return self.actions.add_control_group(group_id)

    def _goto_next_vcs_to_group(self, group_id: int):
        # fulfill the current group
        if self.expected_group_sizes[group_id] > 1:
            self.expected_group_sizes[group_id] = self.expected_group_sizes[group_id] - 1
            self.step = self.step - 3
        # move  to the next group
        elif self.current_group_index < len(self.expected_group_sizes):
            self.current_group_index = self.current_group_index + 1
            self.step = self.step - 3


class FillRefineryOnceBuilt(SmartOrder):

    def __init__(self, base_location: Location, refinery_index: int):
        SmartOrder.__init__(self, base_location)
        self.step = 0
        self.refinery_index = refinery_index
        self.scv_groups = SCVControlGroups()

    def done(self, observations: Observations) -> bool:
        return self.step == 3

    def doable(self, observations: Observations) -> bool:
        refinery_count = BuildingCounter().refineries_count(observations)
        return refinery_count >= self.refinery_index

    def execute(self, observations: Observations) -> actions.FunctionCall:
        if self.step == 0:
            return self._select_refinery()
        elif self.step == 1 and self._selected_refinery_is_built(observations):
            return self._select_vespene_collectors()
        elif self.step == 2:
            return self._send_collectors_to_refinery(observations)

        return self.actions.no_op()

    def _select_refinery(self) -> actions.FunctionCall:
        self.step = self.step + 1
        if self.refinery_index == 1:
            difference_from_cc = BuildingPositionsFromCommandCenter().vespene_geysers()[0]
        else:
            difference_from_cc = BuildingPositionsFromCommandCenter().vespene_geysers()[1]
        cc_y, cc_x = self.location.command_center_first_position()
        target = self.location.transform_distance(
            round(cc_x.mean()),
            difference_from_cc[0],
            round(cc_y.mean()),
            difference_from_cc[1],
        )
        return self.actions.select_point(target)

    def _selected_refinery_is_built(self, observations: Observations) -> bool:
        return observations.single_select().is_built()

    def _select_vespene_collectors(self) -> actions.FunctionCall:
        self.step = self.step + 1
        if self.refinery_index == 1:
            group_id = SCVControlGroups().refinery_one_collectors_group_id()
        else:
            group_id = SCVControlGroups().refinery_two_collectors_group_id()
        return SCVCommonActions().select_a_group_of_scv(group_id)

    def _send_collectors_to_refinery(self, observations: Observations) -> actions.FunctionCall:
        self.step = self.step + 1
        return SCVCommonActions().send_selected_scv_group_to_refinery(self.location, observations, self.refinery_index)


class SendIdleSCVToMineral(SmartOrder):

    def __init__(self, base_location: Location):
        SmartOrder.__init__(self, base_location)
        self.step = 0

    def done(self, observations: Observations) -> bool:
        return self.step == 2

    def doable(self, observations: Observations) -> bool:
        return observations.player().idle_worker_count() > 0 and self._still_minerals_to_collect(observations)

    def execute(self, observations: Observations) -> actions.FunctionCall:
        self.step = self.step + 1
        if self.step == 1:
            return self.actions.select_idle_worker()
        elif self.step == 2:
            return SCVCommonActions().send_scv_to_mineral(observations)

    def _still_minerals_to_collect(self, observations: Observations) -> bool:
        unit_type = observations.screen().unit_type()
        unit_y, unit_x = (unit_type == self.unit_type_ids.neutral_mineral_field()).nonzero()
        if unit_y.any():
            return True
        print("no more mineral (still " +str(observations.player().minerals())+")")
        return False
