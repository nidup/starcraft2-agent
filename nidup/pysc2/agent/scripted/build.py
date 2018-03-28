
from pysc2.lib import actions
from nidup.pysc2.wrapper.actions import TerranActions, TerranActionIds
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.agent.order import Order
from nidup.pysc2.agent.scripted.information import Location
from nidup.pysc2.wrapper.unit_types import UnitTypeIds
from sklearn.cluster import KMeans
import math
import random


class BuildOrder(Order):

    def __init__(self, base_location: Location):
        Order.__init__(self)
        self.base_location = base_location
        self.actions = TerranActions()
        self.action_ids = TerranActionIds()
        self.unit_type_ids = UnitTypeIds()

    def done(self, observations: Observations) -> bool:
        raise NotImplementedError("Should be implemented by concrete order")

    def execute(self, observations: Observations) -> actions.FunctionCall:
        raise NotImplementedError("Should be implemented by concrete order")


class OrdersSequence:
    orders = None
    current_order = None
    current_order_index = None

    def __init__(self, orders):
        self.orders = orders
        self.current_order_index = 0
        self.current_order = self.orders[self.current_order_index]
        # TODO: can avoid this using a proper collection
        for order in self.orders:
            if not isinstance(order, BuildOrder):
                raise ValueError("Expect an instance of Order")

    def current(self, observations: Observations) -> BuildOrder:
        if self.current_order.done(observations):
            self._next_order()
        return self.current_order

    def finished(self, observations: Observations) -> bool:
        return self.current_order.done(observations) and self.current_order_index == len(self.orders) - 1

    def _next_order(self):
        self.current_order_index = self.current_order_index + 1
        self.current_order = self.orders[self.current_order_index]


class BuildSupplyDepot(BuildOrder):

    select_scv_order = False
    supply_depot_built = False
    x_from_base = None
    y_from_base = None

    def __init__(self, base_location, x_from_base, y_from_base):
        BuildOrder.__init__(self, base_location)
        self.x_from_base = x_from_base
        self.y_from_base = y_from_base
        self.select_scv_order = SelectSCV(base_location)

    def done(self, observations: Observations) -> bool:
        return self.supply_depot_built

    def execute(self, observations: Observations) -> actions.FunctionCall:
        if not self.supply_depot_built:
            if not self.select_scv_order.done(observations):
                return self.select_scv_order.execute(observations)
            elif self.action_ids.build_supply_depot() in observations.available_actions():
                cc_y, cc_x = self.base_location.locate_command_center(observations.screen())
                target = self.base_location.transform_distance(
                    int(cc_x.mean()),
                    self.x_from_base,
                    int(cc_y.mean()),
                    self.y_from_base
                )
                self.supply_depot_built = True
                return self.actions.build_supply_depot(target)
        return self.actions.no_op()


class BuildRefinery(BuildOrder):

    builder_scv_selected = False
    refinery_building = False
    refinery_selected = False
    refinery_target = None
    first_collector_scv_selected = False
    first_collector_scv_sent = False
    second_collector_scv_selected = False
    second_collector_scv_sent = False

    def __init__(self, base_location: Location):
        BuildOrder.__init__(self, base_location)
        self.base_location = base_location

    def done(self, observations: Observations) -> bool:
        return self.second_collector_scv_sent

    def execute(self, observations: Observations) -> actions.FunctionCall:
        if not self.builder_scv_selected:
            self.builder_scv_selected = True
            print ("select builder")
            return SelectSCV(self.base_location).execute(observations)
        # https://itnext.io/how-to-locate-and-select-units-in-pysc2-2bb1c81f2ad3
        elif not self.refinery_building and self.action_ids.build_refinery() in observations.available_actions():
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
            self.refinery_building = True
            print ("refinery building")
            return self.actions.build_refinery(self.refinery_target)
        elif self.refinery_building and not self.refinery_selected:
            unit_type = observations.screen().unit_type()
            refinery_y, refinery_x = (unit_type == self.unit_type_ids.terran_refinery()).nonzero()
            if refinery_y.any():
                self.refinery_selected = True
                print ("refinery selected")
                return self.actions.select_point(self.refinery_target)
        elif self.refinery_selected and not self.first_collector_scv_selected:
            if observations.single_select().is_built():
                self.first_collector_scv_selected = True
                print("select first collector")
                return SelectSCV(self.base_location).execute(observations)
        elif self.first_collector_scv_selected and not self.first_collector_scv_sent:
            self.first_collector_scv_sent = True
            print("sent first collector")
            return self.actions.harvest_gather(self.refinery_target)
        elif self.first_collector_scv_sent and not self.second_collector_scv_selected:
            self.second_collector_scv_selected = True
            print("select second collector")
            return SelectSCV(self.base_location).execute(observations)
        elif self.second_collector_scv_selected and not self.second_collector_scv_sent:
            self.second_collector_scv_sent = True
            print("sent second collector")
            return self.actions.harvest_gather(self.refinery_target)

        return self.actions.no_op()


class BuildArmyBuilding(BuildOrder):

    x_from_base = None
    y_from_base = None
    select_scv_order = None
    building_built = False
    building_selected = False
    building_rallied = False

    def __init__(self, base_location, x_from_base, y_from_base):
        BuildOrder.__init__(self, base_location)
        self.x_from_base = x_from_base
        self.y_from_base = y_from_base
        self.select_scv_order = SelectSCV(base_location)

    def done(self, observations: Observations) -> bool:
        return self.building_rallied

    def execute(self, observations: Observations) -> actions.FunctionCall:
        if not self.building_built:
            if self.build_action_id() in observations.available_actions():
                unit_y, unit_x = self.base_location.locate_command_center(observations.screen())
                if unit_x.any():
                    target = self.base_location.transform_distance(
                        int(unit_x.mean()),
                        self.x_from_base,
                        int(unit_y.mean()),
                        self.y_from_base
                    )
                    self.building_built = True
                    return self.build_action(target)
            elif not self.select_scv_order.done(observations):
                return self.select_scv_order.execute(observations)
        elif not self.building_rallied:
            if not self.building_selected:
                unit_type = observations.screen().unit_type()
                unit_y, unit_x = (unit_type == self.building_type()).nonzero()
                if unit_y.any():
                    target = [int(unit_x.mean()), int(unit_y.mean())]
                    self.building_selected = True
                    return self.actions.select_point(target)
            else:
                self.building_rallied = True
                if self.base_location.command_center_is_top_left():
                    target = [29, 21]
                else:
                    target =[29, 46]
                return self.actions.rally_units_minimap(target)
        return self.actions.no_op()

    def building_type(self) -> int:
        raise NotImplementedError("Should be implemented by concrete order")

    def build_action(self, target) -> actions.FunctionCall:
        raise NotImplementedError("Should be implemented by concrete order")

    def build_action_id(self) -> int:
        raise NotImplementedError("Should be implemented by concrete order")


class BuildBarracks(BuildArmyBuilding):

    def __init__(self, base_location, x_from_base, y_from_base):
        BuildArmyBuilding.__init__(self, base_location, x_from_base, y_from_base)

    def building_type(self) -> int:
        return self.unit_type_ids.terran_barracks()

    def build_action(self, target) -> actions.FunctionCall:
        return self.actions.build_barracks(target)

    def build_action_id(self) -> int:
        return self.action_ids.build_barracks()


class BuildFactory(BuildArmyBuilding):

    def __init__(self, base_location, x_from_base, y_from_base):
        BuildArmyBuilding.__init__(self, base_location, x_from_base, y_from_base)

    def building_type(self) -> int:
        return self.unit_type_ids.terran_factory()

    def build_action(self, target) -> actions.FunctionCall:
        return self.actions.build_factory(target)

    def build_action_id(self) -> int:
        return self.action_ids.build_factory()


class MorphOrbitalCommand(BuildOrder):

    command_center_selected = False
    orbital_command_built = False

    def __init__(self, base_location: Location):
        BuildOrder.__init__(self, base_location)

    def done(self, observations: Observations) -> bool:
        return self.orbital_command_built

    def execute(self, observations: Observations) -> actions.FunctionCall:
        if not self.command_center_selected:
            unit_type = observations.screen().unit_type()
            center_y, center_x = (unit_type == self.unit_type_ids.terran_command_center()).nonzero()
            center_x = round(center_x.mean())
            center_y = round(center_y.mean())
            target = [center_x, center_y]
            self.command_center_selected = True
            return self.actions.select_point(target)
        elif self.command_center_selected and self.action_ids.morph_orbital_command() in observations.available_actions():
            self.orbital_command_built = True
            return self.actions.morph_orbital_command()
        return self.actions.no_op()


class BuildTechLabBarracks(BuildOrder):

    barracks_selected = False
    tech_lab_built = False

    def __init__(self, base_location: Location):
        BuildOrder.__init__(self, base_location)

    def done(self, observations: Observations) -> bool:
        return self.tech_lab_built

    def execute(self, observations: Observations) -> actions.FunctionCall:
        if not self.barracks_selected:
            unit_type = observations.screen().unit_type()
            unit_y, unit_x = (unit_type == self.unit_type_ids.terran_barracks()).nonzero()
            target = [int(unit_x.mean()), int(unit_y.mean())]
            self.barracks_selected = True
            return self.actions.select_point(target)
        elif self.action_ids.build_techlab_barracks() in observations.available_actions():
            self.tech_lab_built = True
            unit_type = observations.screen().unit_type()
            unit_y, unit_x = (unit_type == self.unit_type_ids.terran_barracks()).nonzero()
            target = [int(unit_x.mean()), int(unit_y.mean())]
            return self.actions.build_techlab_barracks(target)

        return self.actions.no_op()


class SelectSCV(BuildOrder):

    scv_selected = False

    def __init__(self, base_location: Location):
        BuildOrder.__init__(self, base_location)

    def done(self, observations: Observations) -> bool:
        return self.scv_selected

    def execute(self, observations: Observations) -> actions.FunctionCall:
        if not self.scv_selected:
            if observations.player().idle_worker_count() > 0:
                self.scv_selected = True
                return self.actions.select_idle_worker()
            else:
                unit_type = observations.screen().unit_type()
                unit_y, unit_x = (unit_type == self.unit_type_ids.terran_scv()).nonzero()
                rand_unit_index = random.randint(0, len(unit_y) - 1)
                target = [unit_x[rand_unit_index], unit_y[rand_unit_index]]
                self.scv_selected = True
                return self.actions.select_point(target)
        return self.actions.no_op()


class SendSCVToRefinery(BuildOrder):

    select_scv_order = False
    scv_sent_to_refinery = False

    def __init__(self, base_location: Location):
        BuildOrder.__init__(self, base_location)
        self.select_scv_order = SelectSCV(base_location)

    def done(self, observations: Observations) -> bool:
        return self.scv_sent_to_refinery

    def execute(self, observations: Observations) -> actions.FunctionCall:
        if not self.select_scv_order.done(observations):
            return self.select_scv_order.execute(observations)
        elif self.action_ids.move_screen() in observations.available_actions():
            unit_type = observations.screen().unit_type()
            unit_y, unit_x = (unit_type == self.unit_type_ids.terran_refinery()).nonzero()
            if unit_y.any():
                target = [int(unit_x.mean()), int(unit_y.mean())]
                self.scv_sent_to_refinery = True
                return self.actions.move_screen(target)
        return self.actions.no_op()
