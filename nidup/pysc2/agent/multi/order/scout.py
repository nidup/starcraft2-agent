
from pysc2.lib import actions
from nidup.pysc2.agent.multi.info.player import Location
from nidup.pysc2.wrapper.actions import ActionQueueParameter
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.agent.multi.order.common import SmartOrder, SCVControlGroups, SCVCommonActions


class ScoutWithScv(SmartOrder):

    def __init__(self, base_location: Location):
        SmartOrder.__init__(self, base_location)
        self.step = 0
        self.scv_groups = SCVControlGroups()

    def doable(self, observations: Observations) -> bool:
        return True

    def done(self, observations: Observations) -> bool:
        return self.step == 3

    def execute(self, observations: Observations) -> actions.FunctionCall:
        if self.step == 0:
            return self._select_scout_scv()
        elif self.step == 1:
            return self._send_scout_to_enemy_base()
        elif self.step == 2:
            return self._send_scout_back_to_base()
        return self.actions.no_op()

    def _select_scout_scv(self) -> actions.FunctionCall:
        self.step = self.step + 1
        return SCVCommonActions().select_a_group_of_scv(self.scv_groups.scouting_group_id())

    def _send_scout_to_enemy_base(self) -> actions.FunctionCall:
        self.step = self.step + 1
        other_bases_minimap = self.location.other_unknown_bases_locations_on_minimap()
        target_y, target_x = other_bases_minimap.pop(0)
        target = [target_x, target_y]
        return self.actions.move_minimap(target)

    def _send_scout_back_to_base(self):
        self.step = self.step + 1
        target_y, target_x = self.location.base_location_on_minimap()
        target = [target_x, target_y]
        return self.actions.move_minimap(target, ActionQueueParameter().queued())
