
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.agent.multi.order.common import SmartOrder, NoOrder
from nidup.pysc2.agent.multi.commander.attack import AttackCommander, LateGameAttackCommander
from nidup.pysc2.agent.multi.goal.common import Goal
from nidup.pysc2.agent.multi.info.player import Location


class AttackQuadrantGoal(Goal):

    def __init__(self, attack_commander: AttackCommander):
        self.attack_commander = attack_commander
        self.current_order = None

    def order(self, observations: Observations) -> SmartOrder:
        if not self.current_order:
            self.current_order = self.attack_commander.order(observations)
        if not self.current_order.done(observations):
            return self.current_order

    def done(self, observations: Observations) -> bool:
        return self.current_order and self.current_order.done(observations)


class SeekAndDestroyQuadrantGoal(Goal):

    def __init__(self, location: Location):
        self.location = location
        self.current_order = None
        self.noop_orders = []
        # adding a bunch of noop to let the time to execute the attack order
        for idx in range(0, 20):
            self.noop_orders.append(NoOrder())

    def order(self, observations: Observations) -> SmartOrder:
        if not self.current_order:
            self.current_order = LateGameAttackCommander(self.location).order(observations)
        if not self.current_order.done(observations):
            return self.current_order
        noop_order = self.noop_orders.pop(0)
        return noop_order

    def done(self, observations: Observations) -> bool:
        return len(self.noop_orders) == 0
