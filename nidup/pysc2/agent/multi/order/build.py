
from pysc2.lib import actions
from nidup.pysc2.agent.multi.order.common import SmartOrder, SCVControlGroups, SCVCommonActions, BuildingPositionsFromCommandCenter
from nidup.pysc2.agent.information import Location, BuildingCounter
from nidup.pysc2.wrapper.observations import Observations


class BuildBarrack(SmartOrder):

    def __init__(self, location: Location, barrack_index: int):
        SmartOrder.__init__(self, location)
        self.step = 0
        self.scv_groups = SCVControlGroups()
        self.barrack_index = barrack_index

    def doable(self, observations: Observations) -> bool:
        return observations.player().minerals() >= 150

    def done(self, observations: Observations) -> bool:
        return self.step == 2

    def execute(self, observations: Observations) -> actions.FunctionCall:
        if self.step == 0:
            return self._select_all_mineral_collecter_scv()
        elif self.step == 1:
            return self._build_barracks(observations)

    def _select_all_mineral_collecter_scv(self) -> actions.FunctionCall:
        self.step = self.step + 1
        return SCVCommonActions().select_a_group_of_scv(self.scv_groups.mineral_collectors_group_id())

    def _build_barracks(self, observations: Observations) -> actions.FunctionCall:
        cc_y, cc_x = self.location.command_center_first_position()
        if self.action_ids.build_barracks() in observations.available_actions():
            if cc_y.any():
                self.step = self.step + 1
                current_count_to_difference_from_cc = BuildingPositionsFromCommandCenter().barracks()
                target = self.location.transform_distance(
                    round(cc_x.mean()),
                    current_count_to_difference_from_cc[self.barrack_index - 1][0],
                    round(cc_y.mean()),
                    current_count_to_difference_from_cc[self.barrack_index - 1][1],
                )
                return self.actions.build_barracks(target)

        return self.actions.no_op()


class BuildTechLabBarrack(SmartOrder):

    def __init__(self, base_location: Location, barrack_index: int):
        SmartOrder.__init__(self, base_location)
        self.step = 0
        self.scv_groups = SCVControlGroups()
        self.barrack_index = barrack_index

    def doable(self, observations: Observations) -> bool:
        return observations.player().minerals() >= 50 and observations.player().vespene() >= 25

    def done(self, observations: Observations) -> bool:
        return self.step == 2

    def execute(self, observations: Observations) -> actions.FunctionCall:
        if self.step == 0:
            return self._select_barrack(observations)
        elif self.step == 1:
            return self._build_techlab(observations)
        return self.actions.no_op()

    def _select_barrack(self, observations: Observations) -> actions.FunctionCall:
        barrack_count = BuildingCounter().barracks_count(observations)
        if barrack_count >= 1:
            self.step = self.step + 1
            cc_y, cc_x = self.location.command_center_first_position()
            difference_from_cc = self.difference_from_command_center()
            target = self.location.transform_distance(
                round(cc_x.mean()),
                difference_from_cc[0],
                round(cc_y.mean()),
                difference_from_cc[1],
            )
            return self.actions.select_point(target)
        return self.actions.no_op()

    def _build_techlab(self, observations: Observations) -> actions.FunctionCall:
        if self.action_ids.build_techlab_barracks() in observations.available_actions():
            self.step = self.step + 1
            cc_y, cc_x = self.location.command_center_first_position()
            difference_from_cc = self.difference_from_command_center()
            target = self.location.transform_distance(
                round(cc_x.mean()),
                difference_from_cc[0],
                round(cc_y.mean()),
                difference_from_cc[1],
            )
            return self.actions.build_techlab_barracks(target)
        return self.actions.no_op()

    def difference_from_command_center(self) -> []:
        return BuildingPositionsFromCommandCenter().barracks()[self.barrack_index - 1]


class BuildReactorBarrack(SmartOrder):

    def __init__(self, base_location: Location, barrack_index: int):
        SmartOrder.__init__(self, base_location)
        self.step = 0
        self.scv_groups = SCVControlGroups()
        self.barrack_index = barrack_index

    def doable(self, observations: Observations) -> bool:
        return observations.player().minerals() >= 50 and observations.player().vespene() >= 50

    def done(self, observations: Observations) -> bool:
        return self.step == 2

    def execute(self, observations: Observations) -> actions.FunctionCall:
        if self.step == 0:
            return self._select_barrack(observations)
        elif self.step == 1:
            return self._build_reactor(observations)
        return self.actions.no_op()

    def _select_barrack(self, observations: Observations) -> actions.FunctionCall:
        barrack_count = BuildingCounter().barracks_count(observations)
        if barrack_count >= 2: # always build on second and third barracks
            self.step = self.step + 1
            cc_y, cc_x = self.location.command_center_first_position()
            difference_from_cc = self.difference_from_command_center()
            target = self.location.transform_distance(
                round(cc_x.mean()),
                difference_from_cc[0],
                round(cc_y.mean()),
                difference_from_cc[1],
            )
            return self.actions.select_point(target)
        return self.actions.no_op()

    def _build_reactor(self, observations: Observations) -> actions.FunctionCall:
        if self.action_ids.build_reactor_barracks() in observations.available_actions():
            self.step = self.step + 1
            cc_y, cc_x = self.location.command_center_first_position()
            difference_from_cc = self.difference_from_command_center()
            target = self.location.transform_distance(
                round(cc_x.mean()),
                difference_from_cc[0],
                round(cc_y.mean()),
                difference_from_cc[1],
            )
            return self.actions.build_reactor_barracks(target)
        return self.actions.no_op()

    def difference_from_command_center(self) -> []:
        return BuildingPositionsFromCommandCenter().barracks()[self.barrack_index - 1]


class BuildFactory(SmartOrder):

    def __init__(self, location: Location, max_factories: int = 2):
        SmartOrder.__init__(self, location)
        self.step = 0
        self.max_factories = max_factories
        self.scv_groups = SCVControlGroups()

    def doable(self, observations: Observations) -> bool:
        return observations.player().minerals() >= 150 and observations.player().vespene() >= 100

    def done(self, observations: Observations) -> bool:
        return self.step == 2

    def execute(self, observations: Observations) -> actions.FunctionCall:
        self.step = self.step + 1
        if self.step == 1:
            return self._select_all_mineral_collecter_scv()
        elif self.step == 2:
            return self._build_factory(observations)

    def _select_all_mineral_collecter_scv(self) -> actions.FunctionCall:
        return SCVCommonActions().select_a_group_of_scv(self.scv_groups.mineral_collectors_group_id())

    def _build_factory(self, observations: Observations) -> actions.FunctionCall:
        cc_y, cc_x = self.location.command_center_first_position()
        factories_count = BuildingCounter().factories_count(observations)
        if factories_count < self.max_factories and self.action_ids.build_factory() in observations.available_actions():
            if cc_y.any():
                current_count_to_difference_from_cc = BuildingPositionsFromCommandCenter().factories()
                target = self.location.transform_distance(
                    round(cc_x.mean()),
                    current_count_to_difference_from_cc[factories_count][0],
                    round(cc_y.mean()),
                    current_count_to_difference_from_cc[factories_count][1],
                )
                return self.actions.build_factory(target)
        return self.actions.no_op()


class BuildSupplyDepot(SmartOrder):

    def __init__(self, location: Location, max_supplies: int = 10):
        SmartOrder.__init__(self, location)
        self.step = 0
        self.max_supplies = max_supplies
        self.scv_groups = SCVControlGroups()

    def doable(self, observations: Observations) -> bool:
        return observations.player().minerals() >= 100

    def done(self, observations: Observations) -> bool:
        return self.step == 2

    def execute(self, observations: Observations) -> actions.FunctionCall:
        self.step = self.step + 1
        if self.step == 1:
            return self._select_all_mineral_collecter_scv()
        elif self.step == 2:
            return self._build_supply_depot(observations)

    def _select_all_mineral_collecter_scv(self) -> actions.FunctionCall:
        return SCVCommonActions().select_a_group_of_scv(self.scv_groups.mineral_collectors_group_id())

    def _build_supply_depot(self, observations: Observations) -> actions.FunctionCall:
        cc_y, cc_x = self.location.command_center_first_position()
        supply_depot_count = BuildingCounter().supply_depots_count(observations)
        if supply_depot_count < self.max_supplies and self.action_ids.build_supply_depot() in observations.available_actions():
            if cc_y.any():
                current_count_to_difference_from_cc = BuildingPositionsFromCommandCenter().supply_depots()
                target = self.location.transform_distance(
                    round(cc_x.mean()),
                    current_count_to_difference_from_cc[supply_depot_count][0],
                    round(cc_y.mean()),
                    current_count_to_difference_from_cc[supply_depot_count][1],
                )
                return self.actions.build_supply_depot(target)
        return self.actions.no_op()


class BuildRefinery(SmartOrder):

    def __init__(self, base_location: Location, refinery_index: int):
        SmartOrder.__init__(self, base_location)
        self.step = 0
        self.refinery_index = refinery_index
        self.scv_groups = SCVControlGroups()

    def doable(self, observations: Observations) -> bool:
        return observations.player().minerals() >= 75

    def done(self, observations: Observations) -> bool:
        return self.step == 2

    def execute(self, observations: Observations) -> actions.FunctionCall:
        group_id = self._relevant_group_id()
        self.step = self.step + 1
        if self.step == 1:
            return self._select_all_refinery_collecter_scv(group_id)
        elif self.step == 2:
            return self._build_refinery(observations)
        return self.actions.no_op()

    def _relevant_group_id(self) -> int:
        if self.refinery_index == 1:
            return self.scv_groups.refinery_one_collectors_group_id()
        return self.scv_groups.refinery_two_collectors_group_id()

    def _select_all_refinery_collecter_scv(self, group_id: int) -> actions.FunctionCall:
        return SCVCommonActions().select_a_group_of_scv(group_id)

    def _build_refinery(self, observations: Observations) -> actions.FunctionCall:
        if self.action_ids.build_refinery() in observations.available_actions():
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
            #print(
            #    "build refinery "+str(self.refinery_index) + " on "+str(target[0])+ " "+str(target[1])
            #    + " CC is "+ str(round(cc_x.mean())) + " " + str(round(cc_y.mean()))
            #)

            return self.actions.build_refinery(target)
        return self.actions.no_op()
