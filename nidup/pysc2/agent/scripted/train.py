
from pysc2.lib import actions
from nidup.pysc2.wrapper.actions import TerranActions, TerranActionIds
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.agent.order import Order
from nidup.pysc2.agent.scripted.information import BaseLocation
from nidup.pysc2.wrapper.unit_types import UnitTypeIds


class RepeatableOnceDoneOrder(Order):

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

    def executable(self, observations: Observations) -> bool:
        raise NotImplementedError("Should be implemented by concrete order")


class OrdersRepetition:
    orders = None
    current_order = None
    current_order_index = None

    def __init__(self, orders):
        self.orders = orders
        self.current_order_index = 0
        self.current_order = self.orders[self.current_order_index]
        # TODO: can avoid this using a proper collection
        for order in self.orders:
            if not isinstance(order, RepeatableOnceDoneOrder):
                raise ValueError("Expect an instance of RepeatableOnceDoneOrder")

    def current(self, observations: Observations) -> RepeatableOnceDoneOrder:
        if self.current_order.done(observations):
            self._next_order()
        return self.current_order

    def _next_order(self):
        self.current_order_index = self.current_order_index + 1
        if self.current_order_index < len(self.orders):
            self.current_order = self.orders[self.current_order_index]
        else:
            self.current_order_index = 0
            self.current_order = self.orders[self.current_order_index]


class TrainBarracksUnit(RepeatableOnceDoneOrder):

    amount_trainee = 0
    already_trained = 0
    barracks_selected = False
    army_selected = False
    army_rallied = False

    def __init__(self, base_location, amount):
        RepeatableOnceDoneOrder.__init__(self, base_location)
        self.amount_trainee = amount

    def done(self, observations: Observations) -> bool:
        return (self.already_trained >= self.amount_trainee)\
               or (observations.player().food_used() == observations.player().food_cap())

    def execute(self, observations: Observations) -> actions.FunctionCall:
        if self.done(observations):
            self._reset()
        elif self._train_action_id() in observations.available_actions():
            self.already_trained = self.already_trained + 1
            return self._train_action()
        elif not self.barracks_selected:
            unit_type = observations.screen().unit_type()
            unit_y, unit_x = (unit_type == self.unit_type_ids.terran_barracks()).nonzero()
            if unit_y.any():
                target = [int(unit_x.mean()), int(unit_y.mean())]
                self.barracks_selected = True
                return self.actions.select_point(target)
        return self.actions.no_op()

    def executable(self, observations: Observations) -> bool:
        raise NotImplementedError("Should be implemented by concrete order")

    def _reset(self):
        self.already_trained = 0
        self.barracks_selected = False
        self.army_selected = False
        self.army_rallied = False

    def _train_action(self) -> actions.FunctionCall:
        raise NotImplementedError("Should be implemented by concrete order")

    def _train_action_id(self) -> int:
        raise NotImplementedError("Should be implemented by concrete order")


class TrainMarine(TrainBarracksUnit):

    def __init__(self, base_location, amount):
        TrainBarracksUnit.__init__(self, base_location, amount)

    def executable(self, observations: Observations) -> bool:
        unit_type = observations.screen().unit_type()
        unit_y, unit_x = (unit_type == self.unit_type_ids.terran_barracks()).nonzero()
        if unit_y.any():
            return True
        else:
            return False

    def _train_action(self) -> actions.FunctionCall:
        return self.actions.train_marine()

    def _train_action_id(self) -> int:
        return self.action_ids.train_marine()


class TrainMarauder(TrainBarracksUnit):

    def executable(self, observations: Observations) -> bool:
        unit_type = observations.screen().unit_type()
        unit_y, unit_x = (unit_type == self.unit_type_ids.terran_barracks_techlab()).nonzero()
        if unit_y.any():
            return True
        else:
            return False

    def __init__(self, base_location, amount):
        TrainBarracksUnit.__init__(self, base_location, amount)

    def _train_action(self) -> actions.FunctionCall:
        return self.actions.train_marauder()

    def _train_action_id(self) -> int:
        return self.action_ids.train_marauder()


class PushWithArmy(RepeatableOnceDoneOrder):

    army_selected = False
    push_ordered = False

    def __init__(self, base_location: BaseLocation):
        RepeatableOnceDoneOrder.__init__(self, base_location)

    def done(self, observations: Observations) -> bool:
        return self.push_ordered

    def execute(self, observations: Observations) -> actions.FunctionCall:
        if self.done(observations):
            self._reset()
        elif not self.army_selected:
            if self.action_ids.select_army() in observations.available_actions():
                self.army_selected = True
                return self.actions.select_army()
        elif self.army_selected and self.action_ids.attack_minimap() in observations.available_actions():
            self.push_ordered = True
            if self.base_location.top_left():
                return self.actions.attack_minimap([39, 45])
            return self.actions.attack_minimap([21, 24])
        return self.actions.no_op()

    def executable(self, observations: Observations) -> bool:
        return self.action_ids.select_army() in observations.available_actions()

    def _reset(self):
        self.army_selected = False
        self.push_ordered = False
