
from pysc2.lib import actions
from nidup.pysc2.agent.information import Location, BuildingCounter
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.agent.multi.order.common import SmartOrder


# http://liquipedia.net/starcraft2/Tech_Lab_(Legacy_of_the_Void)
class ResearchCombatShield(SmartOrder):

    def __init__(self, base_location: Location):
        SmartOrder.__init__(self, base_location)
        self.step = 0

    def doable(self, observations: Observations) -> bool:
        return observations.player().minerals() >= 100 and observations.player().vespene() >= 100

    def done(self, observations: Observations) -> bool:
        return self.step == 2

    def execute(self, observations: Observations) -> actions.FunctionCall:
        if self.step == 0:
            return self._select_tech_barrack(observations)
        elif self.step == 1:
            return self._research_combat_shield(observations)
        return self.actions.no_op()

    def _select_tech_barrack(self, observations: Observations) -> actions.FunctionCall:
        techlab_barrack_count = BuildingCounter().techlab_barracks_count(observations)
        if techlab_barrack_count >= 1:
            self.step = self.step + 1
            unit_type = observations.screen().unit_type()
            center_y, center_x = (unit_type == self.unit_type_ids.terran_barracks_techlab()).nonzero()
            center_x = round(center_x.mean())
            center_y = round(center_y.mean())
            target = [center_x, center_y]
            return self.actions.select_point(target)
        return self.actions.no_op()

    def _research_combat_shield(self, observations: Observations) -> actions.FunctionCall:
        if self.action_ids.research_combat_shield() in observations.available_actions():
            self.step = self.step + 1
            return self.actions.research_combat_shield()
        return self.actions.no_op()


# http://liquipedia.net/starcraft2/Tech_Lab_(Legacy_of_the_Void)
class ResearchConcussiveShells(SmartOrder):

    def __init__(self, base_location: Location):
        SmartOrder.__init__(self, base_location)
        self.step = 0

    def doable(self, observations: Observations) -> bool:
        return observations.player().minerals() >= 50 and observations.player().vespene() >= 50

    def done(self, observations: Observations) -> bool:
        return self.step == 2

    def execute(self, observations: Observations) -> actions.FunctionCall:
        if self.step == 0:
            return self._select_tech_barrack(observations)
        elif self.step == 1:
            return self._research_concussive_shells(observations)
        return self.actions.no_op()

    def _select_tech_barrack(self, observations: Observations) -> actions.FunctionCall:
        techlab_barrack_count = BuildingCounter().techlab_barracks_count(observations)
        if techlab_barrack_count >= 1:
            self.step = self.step + 1
            unit_type = observations.screen().unit_type()
            center_y, center_x = (unit_type == self.unit_type_ids.terran_barracks_techlab()).nonzero()
            center_x = round(center_x.mean())
            center_y = round(center_y.mean())
            target = [center_x, center_y]
            return self.actions.select_point(target)
        return self.actions.no_op()

    def _research_concussive_shells(self, observations: Observations) -> actions.FunctionCall:
        if self.action_ids.research_concussive_shells() in observations.available_actions():
            self.step = self.step + 1
            return self.actions.research_concussive_shells()
        return self.actions.no_op()
