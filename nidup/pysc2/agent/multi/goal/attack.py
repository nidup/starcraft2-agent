
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.agent.multi.order.common import SmartOrder
from nidup.pysc2.agent.multi.commander.attack import AttackCommander
from nidup.pysc2.agent.multi.goal.common import Goal


class AttackQuadrantGoal(Goal):

    def __init__(self, attack_commander: AttackCommander):
        self.attack_commander = attack_commander
        self.current_order = None
        self.number_orders = 10
        self.already_done = 0

    def order(self, observations: Observations) -> SmartOrder:
        if not self.current_order:
            self.current_order = self.attack_commander.order(observations)
        if not self.current_order.done(observations):
            return self.current_order
        else:
            self.current_order = self.attack_commander.order(observations)
            self.already_done = self.already_done + 1
        return self.current_order

    def done(self, observations: Observations) -> bool:
        return self.already_done >= self.number_orders
