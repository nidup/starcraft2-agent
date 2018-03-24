
from nidup.pysc2.agent.commander import Commander
from nidup.pysc2.agent.order import Order
from nidup.pysc2.agent.information import BuildingCounter, EnemyDetector
from nidup.pysc2.agent.scripted.camera import CenterCameraOnCommandCenter
from nidup.pysc2.agent.multi.order.common import NoOrder
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.agent.information import Location
from nidup.pysc2.agent.multi.order.build import BuildSupplyDepot
from nidup.pysc2.agent.multi.commander.attack import AttackCommander
from nidup.pysc2.agent.multi.goal.build import BuildOrdersGoalFactory
from nidup.pysc2.agent.multi.goal.attack import AttackQuadrantGoal
from nidup.pysc2.agent.multi.goal.train import TrainSquadGoalFactory


class GoalCommander(Commander):

    def __init__(self, location: Location, agent_name: str, enemy_detector: EnemyDetector, attack_commander: AttackCommander):
        Commander.__init__(self)
        self.location = location
        self.agent_name = agent_name
        self.enemy_detector = enemy_detector
        self.attack_commander = attack_commander
        self.goals = None
        self.current_goal = None
        self.current_order = None

    def order(self, observations: Observations)-> Order:
        # don't start before to know the enemy's race
        if not self.enemy_detector.race_detected():
            return NoOrder()
        if not self.current_goal:
            self.goals = self._prepare_goals(self.location)
            self.current_goal = self.goals.pop(0)
            self.current_order = self.current_goal.order(observations)
        if self.current_goal.done(observations):
            self.current_goal = self.goals.pop(0)
            self.current_order = self.current_goal.order(observations)
            return self._extra_supply_depots(observations)
        elif self.current_order and self.current_order.done(observations):
            self.current_order = None
            return CenterCameraOnCommandCenter(self.location)
        elif self.current_order and not self.current_order.done(observations):
            return self.current_order
        elif not self.current_order:
            self.current_order = self.current_goal.order(observations)
            return self.current_order
        return NoOrder()

    def _prepare_goals(self, location: Location) -> []:
        goals = [BuildOrdersGoalFactory().build_3rax_1techlab_2reactors(location)]
        for repeat in range(0, 100):
            for army in range(0, 2):
                goals = goals + [TrainSquadGoalFactory().train_7marines_3marauders(location)]
            goals = goals + [AttackQuadrantGoal(self.attack_commander)]
        return goals

    def _goal_is_finished(self, observations: Observations) -> bool:
        return self.current_goal.done(observations)

    def _commander_name(self) -> str:
        return self.agent_name + "." + self.__class__.__name__

    def _extra_supply_depots(self, observations: Observations) -> Order:
        counter = BuildingCounter()
        expectMore = counter.supply_depots_count(observations) <= 15
        supplyAlmostFull = observations.player().food_cap() - observations.player().food_used() <= 2
        if expectMore and supplyAlmostFull:
            return BuildSupplyDepot(self.location)
        else:
            return NoOrder()
