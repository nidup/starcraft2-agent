
import random
from pysc2.lib import actions
from nidup.pysc2.agent.order import Order
from nidup.pysc2.agent.smart.information import Location
from nidup.pysc2.wrapper.actions import TerranActions, TerranActionIds
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.wrapper.unit_types import UnitTypeIds


class SmartOrder(Order):
    def __init__(self, location: Location):
        Order.__init__(self)
        self.location = location
        self.actions = TerranActions()
        self.action_ids = TerranActionIds()
        self.unit_type_ids = UnitTypeIds()

    def done(self, observations: Observations) -> bool:
        raise NotImplementedError("Should be implemented by concrete order")

    def execute(self, observations: Observations) -> actions.FunctionCall:
        raise NotImplementedError("Should be implemented by concrete order")


class SCVCommonActions:

    def __init__(self):
        self.actions = TerranActions()
        self.action_ids = TerranActionIds()
        self.unit_type_ids = UnitTypeIds()

    def select_scv(self, observations: Observations) -> actions.FunctionCall:
        unit_type = observations.screen().unit_type()
        unit_y, unit_x = (unit_type == self.unit_type_ids.terran_scv()).nonzero()
        if unit_y.any():
            i = random.randint(0, len(unit_y) - 1)
            target = [unit_x[i], unit_y[i]]
            return self.actions.select_point(target)

        return self.actions.no_op()

    def send_scv_to_mineral(self, observations: Observations) -> actions.FunctionCall:
        if self.action_ids.harvest_gather() in observations.available_actions():
            unit_type = observations.screen().unit_type()
            unit_y, unit_x = (unit_type == self.unit_type_ids.neutral_mineral_field()).nonzero()
            if unit_y.any():
                i = random.randint(0, len(unit_y) - 1)
                m_x = unit_x[i]
                m_y = unit_y[i]
                target = [int(m_x), int(m_y)]
                return self.actions.harvest_gather(target)
        return self.actions.no_op()


class BuildBarracks(SmartOrder):

    def __init__(self, location: Location):
        SmartOrder.__init__(self, location)
        self.step = 0

    def done(self, observations: Observations) -> bool:
        return self.step == 3

    def execute(self, observations: Observations) -> actions.FunctionCall:
        self.step = self.step + 1
        if self.step == 1:
            return self.select_scv(observations)
        elif self.step == 2:
            return self.build(observations)
        elif self.step == 3:
            return self.send_scv_to_mineral(observations)

    def select_scv(self, observations: Observations) -> actions.FunctionCall:
        return SCVCommonActions().select_scv(observations)

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

    def send_scv_to_mineral(self, observations: Observations) -> actions.FunctionCall:
        return SCVCommonActions().send_scv_to_mineral(observations)


class BuildSupplyDepot(SmartOrder):

    def __init__(self, location: Location):
        SmartOrder.__init__(self, location)
        self.step = 0

    def done(self, observations: Observations) -> bool:
        return self.step == 3

    def execute(self, observations: Observations) -> actions.FunctionCall:
        self.step = self.step + 1
        if self.step == 1:
            return self.select_scv(observations)
        elif self.step == 2:
            return self.build(observations)
        elif self.step == 3:
            return self.send_scv_to_mineral(observations)

    def select_scv(self, observations: Observations) -> actions.FunctionCall:
        return SCVCommonActions().select_scv(observations)

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

    def send_scv_to_mineral(self, observations: Observations) -> actions.FunctionCall:
        return SCVCommonActions().send_scv_to_mineral(observations)


class BuildMarine(SmartOrder):

    def __init__(self, location: Location):
        SmartOrder.__init__(self, location)
        self.step = 0

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


class Attack(SmartOrder):

    def __init__(self, location: Location, x , y):
        SmartOrder.__init__(self, location)
        self.step = 0
        self.x = x
        self.y = y

    def done(self, observations: Observations) -> bool:
        return self.step == 2

    def execute(self, observations: Observations) -> actions.FunctionCall:
        self.step = self.step + 1
        if self.step == 1:
            return self.select_army(observations)
        elif self.step == 2:
            return self.attack_minimap(observations)

    def select_army(self, observations: Observations) -> actions.FunctionCall:
        if self.action_ids.select_army() in observations.available_actions():
            return self.actions.select_army()

        return self.actions.no_op()

    def attack_minimap(self, observations: Observations) -> actions.FunctionCall:
        do_it = True
        if len(observations.single_select()) > 0 and observations.single_select()[0][0] == self.unit_type_ids.terran_scv():
            do_it = False
        if len(observations.multi_select()) > 0 and observations.multi_select()[0][0] == self.unit_type_ids.terran_scv():
            do_it = False

        if do_it and self.action_ids.attack_minimap() in observations.available_actions():
            x_offset = random.randint(-1, 1)
            y_offset = random.randint(-1, 1)
            target = self.location.transform_location(int(self.x) + (x_offset * 8), int(self.y) + (y_offset * 8))
            return self.actions.attack_minimap(target)

        return self.actions.no_op()


class NoOrder(Order):

    def __init__(self):
        Order.__init__(self)
        self.step = 0

    def done(self, observations: Observations) -> bool:
        return self.step == 1

    def execute(self, observations: Observations) -> actions.FunctionCall:
        self.step = self.step + 1
        if self.step == 1:
            return self.do_nothing()

    def do_nothing(self) -> actions.FunctionCall:
        return TerranActions().no_op()
