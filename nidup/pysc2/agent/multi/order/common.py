
import random
from pysc2.lib import actions
from nidup.pysc2.agent.order import Order
from nidup.pysc2.agent.information import Location
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

    def doable(self, observations: Observations) -> bool:
        raise NotImplementedError("Should be implemented by concrete order")

    def done(self, observations: Observations) -> bool:
        raise NotImplementedError("Should be implemented by concrete order")

    def execute(self, observations: Observations) -> actions.FunctionCall:
        raise NotImplementedError("Should be implemented by concrete order")


class NoOrder(SmartOrder):

    def __init__(self):
        SmartOrder.__init__(self, None)
        self.step = 0

    def doable(self, observations: Observations) -> bool:
        return True

    def done(self, observations: Observations) -> bool:
        return self.step == 1

    def execute(self, observations: Observations) -> actions.FunctionCall:
        self.step = self.step + 1
        if self.step == 1:
            return self.do_nothing()

    def do_nothing(self) -> actions.FunctionCall:
        return TerranActions().no_op()


class SCVControlGroups:

    def all_group_id(self) -> int:
        return 0

    def mineral_collectors_group_id(self) -> int:
        return 1

    def refinery_one_collectors_group_id(self) -> int:
        return 2

    def refinery_two_collectors_group_id(self) -> int:
        return 3


class SCVCommonActions:

    def __init__(self):
        self.actions = TerranActions()
        self.action_ids = TerranActionIds()
        self.unit_type_ids = UnitTypeIds()

    def select_a_group_of_scv(self, group_id: int) -> actions.FunctionCall:
        return self.actions.select_control_group(group_id)

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

    def send_selected_scv_group_to_refinery(self, location: Location, observations: Observations, refinery_id: int) -> actions.FunctionCall:
        if self.action_ids.harvest_gather() in observations.available_actions():
            if refinery_id == 1:
                difference_from_cc = BuildingPositionsFromCommandCenter().vespene_geysers()[0]
            else:
                difference_from_cc = BuildingPositionsFromCommandCenter().vespene_geysers()[1]
            cc_y, cc_x = location.command_center_first_position()
            target = location.transform_distance(
                round(cc_x.mean()),
                difference_from_cc[0],
                round(cc_y.mean()),
                difference_from_cc[1],
            )
            #print("send collector " + str(refinery_id) + " to refinery " + str(target[0]) + " " + str(target[1]))
            return self.actions.harvest_gather(target)
        return self.actions.no_op()


class BuildingPositionsFromCommandCenter:

    def supply_depots(self) -> []:
        # some tweak to make it work on both start positions that seems not symetric
        return [
            [-35, -20],
            [-35, -10],
            [-35, 0],
            [-35, 10],
            [-35, 20],
            [-25, -30],
            [-15, -30],
            [-5, -30],
            [5, -35],
            [15, -35]
        ]

    # keeping space for techlab/reactor on each
    def barracks(self) -> []:
        return [
            [15, -10],
            [30, -20],
            [20, 10],
            [30, 20],
        ]

    def factories(self) -> []:
        return [
            [10, 25],
            [30, 25], # check it, could not work
        ]

    def vespene_geysers(self) -> []:
        return [
            [10, -22],
            [-24, 12]
        ]

    def refineries(self) -> []:
        return self.vespene_geysers()