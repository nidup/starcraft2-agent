
import math
import random
from pysc2.lib import actions
from nidup.pysc2.agent.order import Order
from nidup.pysc2.agent.information import Location, BuildingCounter
from nidup.pysc2.wrapper.actions import TerranActions, TerranActionIds
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.wrapper.unit_types import UnitTypeIds
from sklearn.cluster import KMeans


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


class SCVControlGroups:

    def all_group_id(self) -> int:
        return 0

    def builders_group_id(self) -> int:
        return 1

    def mineral_collectors_group_id(self) -> int:
        return 2

    def refinery_one_collectors_group_id(self) -> int:
        return 3

    def refinery_two_collectors_group_id(self) -> int:
        return 4


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

    def barracks(self) -> []:
        return [
            [15, -10],
            [30, -20], # keep space for techlab on first barracks
            [15, 10],
            [30, 10],
        ]

    def factories(self) -> []:
        return [
            [15, 25],
            [30, 25],
        ]

# Groups all scv to specialized group to facilitate the further selections of dedicated workers, at the end of this
# order, control groups look like the following
# print(observations.control_groups())
# [[45 12] <- all scv
#  [45  3] <- builder scv
#  [45  3] <- mineral scv
#  [45  3] <- vespene1 scv
#  [45  3] <- vespene2 scv
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
        self.builder_group_id = groups.builders_group_id()
        self.mineral_group_id = groups.mineral_collectors_group_id()
        self.vespene_group1_id = groups.refinery_one_collectors_group_id()
        self.vespene_group2_id = groups.refinery_two_collectors_group_id()
        self.expected_group_sizes = {
            self.builder_group_id: 3,
            self.mineral_group_id: 3,
            self.vespene_group1_id: 3,
            self.vespene_group2_id: 3,
        }
        self.scv_index_in_all_group = 0
        self.current_group_index = 1

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


class SCVCommonActions:

    def __init__(self):
        self.actions = TerranActions()
        self.action_ids = TerranActionIds()
        self.unit_type_ids = UnitTypeIds()

    def select_a_group_of_scv(self, group_id: int) -> actions.FunctionCall:
        return self.actions.select_control_group(group_id)

    def select_a_scv_from_the_current_selected_group(self, observations: Observations, group_id: int) -> actions.FunctionCall:
        if self.action_ids.select_unit() in observations.available_actions():
            group_size = observations.control_groups()[group_id][1]
            random_scv_index = random.randint(0, group_size - 1)
            return self.actions.select_unit(random_scv_index)

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

    def send_scv_to_refinery(self, observations: Observations) -> actions.FunctionCall:
        if self.action_ids.harvest_gather() in observations.available_actions():
            unit_type = observations.screen().unit_type()
            refinery_y, refinery_x = (unit_type == self.unit_type_ids.terran_refinery()).nonzero()
            refinery_count = int(math.ceil(len(refinery_y) / 97))
            if refinery_count > 0:
                units = []
                for i in range(0, len(refinery_y)):
                    units.append((refinery_x[i], refinery_y[i]))
                kmeans = KMeans(refinery_count)
                kmeans.fit(units)
                refinery1_x = int(kmeans.cluster_centers_[0][0])
                refinery1_y = int(kmeans.cluster_centers_[0][1])
                refinery_target = [refinery1_x, refinery1_y]
                return self.actions.harvest_gather(refinery_target)
        return self.actions.no_op()


class BuildBarrack(SmartOrder):

    def __init__(self, location: Location, max_barracks: int = 4):
        SmartOrder.__init__(self, location)
        self.step = 0
        self.scv_groups = SCVControlGroups()
        self.max_barracks = max_barracks

    def done(self, observations: Observations) -> bool:
        return self.step == 4

    def execute(self, observations: Observations) -> actions.FunctionCall:
        self.step = self.step + 1
        if self.step == 1:
            return self._select_all_mineral_collecter_scv()
        elif self.step == 2:
            return self._select_a_mineral_collecter_scv()
        elif self.step == 3:
            return self._build_barracks(observations)
        elif self.step == 4:
            return self._send_collecter_scv_to_mineral(observations)

    def _select_all_mineral_collecter_scv(self) -> actions.FunctionCall:
        return SCVCommonActions().select_a_group_of_scv(self.scv_groups.mineral_collectors_group_id())

    def _select_a_mineral_collecter_scv(self) -> actions.FunctionCall:
        return SCVCommonActions().select_a_group_of_scv(self.scv_groups.mineral_collectors_group_id())

    def _build_barracks(self, observations: Observations) -> actions.FunctionCall:
        cc_y, cc_x = self.location.command_center_first_position()
        barracks_count = BuildingCounter().barracks_count(observations)
        if barracks_count < self.max_barracks and self.action_ids.build_barracks() in observations.available_actions():
            if cc_y.any():
                current_count_to_difference_from_cc = BuildingPositionsFromCommandCenter().barracks()
                target = self.location.transform_distance(
                    round(cc_x.mean()),
                    current_count_to_difference_from_cc[barracks_count][0],
                    round(cc_y.mean()),
                    current_count_to_difference_from_cc[barracks_count][1],
                )
                return self.actions.build_barracks(target)

        return self.actions.no_op()

    def _send_collecter_scv_to_mineral(self, observations: Observations) -> actions.FunctionCall:
        return SCVCommonActions().send_scv_to_mineral(observations)


class BuildTechLabBarrack(SmartOrder):

    def __init__(self, base_location: Location, max_techlab: int = 1):
        SmartOrder.__init__(self, base_location)
        self.step = 0
        self.scv_groups = SCVControlGroups()
        self.max_techlab = max_techlab

    def done(self, observations: Observations) -> bool:
        return self.step == 2

    def execute(self, observations: Observations) -> actions.FunctionCall:
        self.step = self.step + 1
        if self.step == 1:
            return self._select_barrack()
        elif self.step == 2:
            return self._build_techlab(observations)
        return self.actions.no_op()

    def _select_barrack(self) -> actions.FunctionCall:
        cc_y, cc_x = self.location.command_center_first_position()
        difference_from_cc = self.difference_from_command_center()
        target = self.location.transform_distance(
            round(cc_x.mean()),
            difference_from_cc[0],
            round(cc_y.mean()),
            difference_from_cc[1],
        )
        return self.actions.select_point(target)

    def _build_techlab(self, observations: Observations) -> actions.FunctionCall:
        if self.action_ids.build_techlab_barracks() in observations.available_actions():
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
        return BuildingPositionsFromCommandCenter().barracks()[0]


class BuildFactory(SmartOrder):

    def __init__(self, location: Location, max_factories: int = 2):
        SmartOrder.__init__(self, location)
        self.step = 0
        self.max_factories = max_factories
        self.scv_groups = SCVControlGroups()

    def done(self, observations: Observations) -> bool:
        return self.step == 4

    def execute(self, observations: Observations) -> actions.FunctionCall:
        #print("factory")
        self.step = self.step + 1
        if self.step == 1:
            return self._select_all_mineral_collecter_scv()
        elif self.step == 2:
            return self._select_a_mineral_collecter_scv()
        elif self.step == 3:
            return self._build_factory(observations)
        elif self.step == 4:
            return self._send_collecter_scv_to_mineral(observations)

    def _select_all_mineral_collecter_scv(self) -> actions.FunctionCall:
        return SCVCommonActions().select_a_group_of_scv(self.scv_groups.mineral_collectors_group_id())

    def _select_a_mineral_collecter_scv(self) -> actions.FunctionCall:
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

    def _send_collecter_scv_to_mineral(self, observations: Observations) -> actions.FunctionCall:
        return SCVCommonActions().send_scv_to_mineral(observations)


class BuildSupplyDepot(SmartOrder):

    def __init__(self, location: Location, max_supplies: int = 10):
        SmartOrder.__init__(self, location)
        self.step = 0
        self.max_supplies = max_supplies
        self.scv_groups = SCVControlGroups()

    def done(self, observations: Observations) -> bool:
        return self.step == 4

    def execute(self, observations: Observations) -> actions.FunctionCall:
        self.step = self.step + 1
        if self.step == 1:
            return self._select_all_mineral_collecter_scv()
        elif self.step == 2:
            return self._select_a_mineral_collecter_scv()
        elif self.step == 3:
            return self._build_supply_depot(observations)
        elif self.step == 4:
            return self._send_collecter_scv_to_mineral(observations)

    def _select_all_mineral_collecter_scv(self) -> actions.FunctionCall:
        return SCVCommonActions().select_a_group_of_scv(self.scv_groups.mineral_collectors_group_id())

    def _select_a_mineral_collecter_scv(self) -> actions.FunctionCall:
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

    def _send_collecter_scv_to_mineral(self, observations: Observations) -> actions.FunctionCall:
        return SCVCommonActions().send_scv_to_mineral(observations)


class BuildRefinery(SmartOrder):

    def __init__(self, base_location: Location, max_refineries: int = 2):
        SmartOrder.__init__(self, base_location)
        self.step = 0
        self.refinery_target = None
        self.max_refineries = max_refineries
        self.scv_groups = SCVControlGroups()

    def done(self, observations: Observations) -> bool:
        return self.step == 3

    def execute(self, observations: Observations) -> actions.FunctionCall:
        self.step = self.step + 1
        group_id = self._relevant_group_id(observations)
        if self.step == 1:
            return self._select_all_refinery_collecter_scv(group_id)
        elif self.step == 2:
            return self._select_a_refinery_collecter_scv(group_id)
        elif self.step == 3:
            return self._build_refinery(observations)
        return self.actions.no_op()

    def _relevant_group_id(self, observations: Observations) -> int:
        if self._count_refineries(observations) == 0:
            return self.scv_groups.refinery_one_collectors_group_id()
        return self.scv_groups.refinery_two_collectors_group_id()

    def _count_refineries(self, observations: Observations) -> int:
        return BuildingCounter().refineries_count(observations)

    def _select_all_refinery_collecter_scv(self, group_id: int) -> actions.FunctionCall:
        return SCVCommonActions().select_a_group_of_scv(group_id)

    def _select_a_refinery_collecter_scv(self, group_id: int) -> actions.FunctionCall:
        return SCVCommonActions().select_a_group_of_scv(group_id)

    def _build_refinery(self, observations: Observations) -> actions.FunctionCall:
        if self.action_ids.build_refinery() in observations.available_actions():
            unit_type = observations.screen().unit_type()
            vespene_y, vespene_x = (unit_type == self.unit_type_ids.neutral_vespene_geyser()).nonzero()
            vespene_geyser_count = int(math.ceil(len(vespene_y) / 97))
            units = []
            for i in range(0, len(vespene_y)):
                units.append((vespene_x[i], vespene_y[i]))
            kmeans = KMeans(vespene_geyser_count)
            kmeans.fit(units)
            vespene1_x = int(kmeans.cluster_centers_[0][0])
            vespene1_y = int(kmeans.cluster_centers_[0][1])
            self.refinery_target = [vespene1_x, vespene1_y]
            return self.actions.build_refinery(self.refinery_target)
        return self.actions.no_op()


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


class BuildMarauder(SmartOrder):

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
        if self.action_ids.train_marauder() in observations.available_actions():
            return self.actions.train_marauder()
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
        if not observations.single_select().empty() and observations.single_select().unit_type() == self.unit_type_ids.terran_scv():
            do_it = False
        if not observations.multi_select().empty() and observations.multi_select().unit_type(0) == self.unit_type_ids.terran_scv():
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
