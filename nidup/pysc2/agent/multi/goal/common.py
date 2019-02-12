
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.agent.multi.order.common import SmartOrder, NoOrder


class Goal:

    def order(self, observations: Observations) -> SmartOrder:
        raise NotImplementedError("Should be implemented by concrete goal")

    def done(self, observations: Observations) -> bool:
        raise NotImplementedError("Should be implemented by concrete goal")


class OrderedGoal(Goal):

    def __init__(self, orders: []):
        self.orders = orders
        self.current_order = orders.pop(0)

    def order(self, observations: Observations) -> SmartOrder:
        if not self.current_order.done(observations):
            return self.current_order

        order = self.orders[0]
        if order.doable(observations):
            self.current_order = order
            self.orders.pop(0)
            return self.current_order

        return NoOrder()

    def done(self, observations: Observations) -> bool:
        return len(self.orders) == 0
