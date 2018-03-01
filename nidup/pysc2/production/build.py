
from pysc2.lib import actions
from nidup.pysc2.actions import TerranActions, TerranActionIds
from nidup.pysc2.observations import Observations
from nidup.pysc2.order import Order
from nidup.pysc2.information import BaseLocation
from nidup.pysc2.unit_types import UnitTypeIds
from sklearn.cluster import KMeans
import math


class BuildOrder(Order):

    def __init__(self, base_location: BaseLocation):
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


class CenterCameraOnCommandCenter(BuildOrder):
    centered_on_base = False

    def __init__(self, base_location):
        BuildOrder.__init__(self, base_location)

    def done(self, observations: Observations) -> bool:
        return self.centered_on_base

    def execute(self, observations: Observations) -> actions.FunctionCall:
        if not self.centered_on_base:
            unit_y, unit_x = self.base_location.base_location_on_minimap()
            target = [unit_x, unit_y]
            self.centered_on_base = True
            return self.actions.move_camera(target)
        return self.actions.no_op()


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
                unit_y, unit_x = self.base_location.locate_command_center(observations.screen())
                target = self.base_location.transform_location(
                    int(unit_x.mean()),
                    self.x_from_base,
                    int(unit_y.mean()),
                    self.y_from_base
                )
                self.supply_depot_built = True
                return self.actions.build_supply_depot(target)
        return self.actions.no_op()


class BuildRefinery(BuildOrder):

    select_scv_order = None
    refinery_built = False

    def __init__(self, base_location: BaseLocation):
        BuildOrder.__init__(self, base_location)
        self.select_scv_order = SelectSCV(base_location)

    def done(self, observations: Observations) -> bool:
        return self.refinery_built

    def execute(self, observations: Observations) -> actions.FunctionCall:
        if not self.refinery_built:
            if not self.select_scv_order.done(observations):
                return self.select_scv_order.execute(observations)
            # https://itnext.io/how-to-locate-and-select-units-in-pysc2-2bb1c81f2ad3
            elif self.action_ids.build_refinery() in observations.available_actions():
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
                target = [vespene1_x, vespene1_y]
                self.refinery_built = True
                return self.actions.build_refinery(target)
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
                    target = self.base_location.transform_location(
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
                if self.base_location.top_left():
                    return self.actions.rally_units_minimap([29, 21])
                return self.actions.rally_units_minimap([29, 46])
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

    def __init__(self, base_location: BaseLocation):
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

    def __init__(self, base_location: BaseLocation):
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

    def __init__(self, base_location: BaseLocation):
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
                target = [unit_x[0], unit_y[0]]
                self.scv_selected = True
                return self.actions.select_point(target)
        return self.actions.no_op()


class SendSCVToRefinery(BuildOrder):

    select_scv_order = False
    scv_sent_to_refinery = False

    def __init__(self, base_location: BaseLocation):
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