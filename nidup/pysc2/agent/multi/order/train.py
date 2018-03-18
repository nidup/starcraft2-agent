
import random
from pysc2.lib import actions
from nidup.pysc2.agent.information import Location
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.agent.multi.order.common import SmartOrder


class BuildSCV(SmartOrder):

    def __init__(self, location: Location):
        SmartOrder.__init__(self, location)
        self.step = 0

    def doable(self, observations: Observations) -> bool:
        return observations.player().minerals() >= 50

    def done(self, observations: Observations) -> bool:
        return self.step == 2

    def doable(self, observations: Observations) -> bool:
        return observations.player().food_used() < observations.player().food_cap()

    def execute(self, observations: Observations) -> actions.FunctionCall:
        self.step = self.step + 1
        if self.step == 1:
            return self._select_command_center(observations)
        elif self.step == 2:
            return self._train_scv(observations)

    def _select_command_center(self, observations: Observations) -> actions.FunctionCall:
        unit_type = observations.screen().unit_type()
        cc_y, cc_x = (unit_type == self.unit_type_ids.terran_command_center()).nonzero()
        if cc_y.any():
            target = [round(cc_x.mean()), round(cc_y.mean())]
            return self.actions.select_point(target)
        return self.actions.no_op()

    def _train_scv(self, observations: Observations) -> actions.FunctionCall:
        if self.action_ids.train_scv() in observations.available_actions():
            return self.actions.train_scv()
        return self.actions.no_op()


class BuildMarine(SmartOrder):

    def __init__(self, location: Location):
        SmartOrder.__init__(self, location)
        self.step = 0

    def doable(self, observations: Observations) -> bool:
        return observations.player().minerals() >= 50

    def done(self, observations: Observations) -> bool:
        return self.step == 2

    def execute(self, observations: Observations) -> actions.FunctionCall:
        self.step = self.step + 1
        if self.step == 1:
            return self.select_barracks(observations)
        elif self.step == 2:
            return self.train_marine(observations)

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


class BuildMarauder(SmartOrder):

    def __init__(self, location: Location):
        SmartOrder.__init__(self, location)
        self.step = 0

    def doable(self, observations: Observations) -> bool:
        return observations.player().minerals() >= 100 and observations.player().vespene() >= 25

    def done(self, observations: Observations) -> bool:
        return self.step == 2

    def execute(self, observations: Observations) -> actions.FunctionCall:
        self.step = self.step + 1
        if self.step == 1:
            return self.select_barracks(observations)
        elif self.step == 2:
            return self.train_marine(observations)

    def select_barracks(self, observations: Observations) -> actions.FunctionCall:
        unit_type = observations.screen().unit_type()
        barracks_y, barracks_x = (unit_type == self.unit_type_ids.terran_barracks()).nonzero()
        if barracks_y.any():
            i = random.randint(0, len(barracks_y) - 1)
            target = [barracks_x[i], barracks_y[i]]
            return self.actions.select_point_all(target)
        return self.actions.no_op()

    def train_marine(self, observations: Observations) -> actions.FunctionCall:
        if self.action_ids.train_marauder() in observations.available_actions():
            return self.actions.train_marauder()
        return self.actions.no_op()
