
from nidup.pysc2.agent.commander import Commander
from nidup.pysc2.agent.order import Order
from nidup.pysc2.agent.multi.info.enemy import EnemyRaceDetector
from nidup.pysc2.agent.multi.info.player import BuildingCounter
from nidup.pysc2.agent.multi.order.camera import CenterCameraOnCommandCenter
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.wrapper.unit_types import UnitTypeIds
from nidup.pysc2.agent.multi.info.player import Location
from nidup.pysc2.agent.multi.commander.attack import AttackCommander
from nidup.pysc2.agent.multi.order.common import NoOrder
from nidup.pysc2.agent.multi.order.build import BuildSupplyDepot
from nidup.pysc2.agent.multi.goal.build import BuildOrdersGoalFactory
from nidup.pysc2.agent.multi.goal.attack import AttackQuadrantGoal, SeekAndDestroyQuadrantGoal
from nidup.pysc2.agent.multi.goal.train import TrainSquadGoalFactory, TrainSquadGoalProvider, TrainSquadGoal


class GoalCommander(Commander):

    def __init__(self, location: Location, agent_name: str, enemy_detector: EnemyRaceDetector):
        Commander.__init__(self)
        self.location = location
        self.agent_name = agent_name
        self.enemy_detector = enemy_detector
        self.attack_commander = AttackCommander(location, agent_name, enemy_detector)
        self.goals = self._prepare_goals(self.location)
        self.current_goal = None
        self.current_order = None
        self.constant_attack_mode = False
        self.train_squad_goal_provider = TrainSquadGoalProvider(location, agent_name, enemy_detector)

    def order(self, observations: Observations)-> Order:
        # don't start before to know the enemy's race
        if not self.enemy_detector.race_detected():
            return NoOrder()

        if not self.constant_attack_mode and self._move_to_constant_attack_mode(observations):
            self.constant_attack_mode = True
            self.goals = self._prepare_attack_only_goals()
            self.current_goal = None
            self.current_order = None

        if self.current_order and not self.current_order.done(observations):
            return self.current_order

        if not self.current_goal:
            self.current_goal = self.goals.pop(0)
            # TODO hacky hack to replace harcoded goal on the fly
            if isinstance(self.current_goal, TrainSquadGoal):
                self.current_goal = self.train_squad_goal_provider.goal(observations)

            self.current_order = CenterCameraOnCommandCenter(self.location)
            return self.current_order

        if self.current_goal.done(observations):
            self.current_goal = None
            self.current_order = self._extra_supply_depots(observations)
            return self.current_order

        if self.current_order.done(observations):
            self.current_order = self.current_goal.order(observations)
            return self.current_order

        raise RuntimeError("this case should never happen!")

    def learn_on_last_episode_step(self, observations: Observations):
        self.attack_commander.learn_on_last_episode_step(observations)
        self.train_squad_goal_provider.learn_on_last_episode_step(observations)

    def _prepare_goals(self, location: Location) -> []:
        goals = [BuildOrdersGoalFactory().build_3rax_1techlab_2reactors(location)]
        for repeat in range(0, 100):
            for army in range(0, 2):
                goals = goals + [TrainSquadGoalFactory().train_7marines_3marauders(location)]
            goals = goals + [AttackQuadrantGoal(self.attack_commander)]
        return goals

    def _prepare_attack_only_goals(self) -> []:
        goals = []
        for repeat in range(0, 1000):
            goals = goals + [SeekAndDestroyQuadrantGoal(self.location)]
        return goals

    def _goal_is_finished(self, observations: Observations) -> bool:
        return self.current_goal.done(observations)

    def _commander_name(self) -> str:
        return self.agent_name + "." + self.__class__.__name__

    def _needs_extra_supply_depots(self, observations: Observations) -> bool:
        counter = BuildingCounter()
        expectMore = counter.supply_depots_count(observations) <= 15
        supplyAlmostFull = observations.player().food_cap() - observations.player().food_used() <= 2
        return expectMore and supplyAlmostFull

    def _extra_supply_depots(self, observations: Observations) -> Order:
        if self._needs_extra_supply_depots(observations):
            return BuildSupplyDepot(self.location)
        else:
            return NoOrder()

    def _move_to_constant_attack_mode(self, observations: Observations):
        return self._no_more_minerals_to_collect(observations) and self._not_much_minerals_to_spend(observations)

    def _no_more_minerals_to_collect(self, observations: Observations) -> bool:
        unit_type = observations.screen().unit_type()
        unit_type_ids = UnitTypeIds()
        unit_y, unit_x = (unit_type == unit_type_ids.neutral_mineral_field()).nonzero()
        if unit_y.any():
            return False
        return True

    def _not_much_minerals_to_spend(self, observations: Observations) -> bool:
        return observations.player().minerals() <= 200
