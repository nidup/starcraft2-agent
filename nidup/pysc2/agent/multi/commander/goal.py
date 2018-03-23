
import numpy as np
from nidup.pysc2.agent.commander import Commander
from nidup.pysc2.learning.qlearning import QLearningTable, QLearningTableStorage
from nidup.pysc2.agent.order import Order
from nidup.pysc2.agent.information import BuildingCounter, EnemyDetector, RaceNames
from nidup.pysc2.agent.scripted.camera import CenterCameraOnCommandCenter
from nidup.pysc2.agent.multi.order.common import NoOrder
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.agent.information import Location
from nidup.pysc2.agent.multi.order.common import SmartOrder
from nidup.pysc2.agent.multi.order.build import BuildSupplyDepot, BuildBarrack, BuildRefinery, BuildTechLabBarrack, BuildReactorBarrack, BuildFactory, BuildStarport
from nidup.pysc2.agent.multi.order.train import BuildMarine, BuildMarauder, BuildHellion, BuildMedivac
from nidup.pysc2.agent.multi.order.research import ResearchCombatShield, ResearchConcussiveShells
from nidup.pysc2.agent.multi.commander.common import TrainActionsSet, TrainActionsSetRegistry
from nidup.pysc2.agent.multi.order.attack import DumbAttack, QLearningAttack
from nidup.pysc2.agent.multi.commander.attack import AttackCommander


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
        goals = [
            OrderedGoal(
                [
                    BuildSupplyDepot(location),
                    BuildRefinery(location, 1),
                    BuildBarrack(location, 1),
                    BuildSupplyDepot(location),
                    BuildBarrack(location, 2),
                    BuildTechLabBarrack(location, 1),
                    BuildBarrack(location, 3),
                    ResearchCombatShield(location),
                    # BuildMarauder(location),
                    BuildReactorBarrack(location, 2),
                    BuildReactorBarrack(location, 3),
                    BuildSupplyDepot(location),
                    # BuildMarauder(location),
                    # BuildMarine(location),
                    # BuildMarine(location),
                    # BuildMarine(location),
                    # BuildMarine(location),
                    # DumbAttack(location, 15, 47),
                    # BuildFactory(location, 1),
                    # DumbAttack(location, 15, 47),
                    # BuildStarport(location, 1),
                    # DumbAttack(location, 15, 47),
                    # BuildSupplyDepot(location),
                    # BuildSupplyDepot(location),
                    # BuildMarauder(location),
                    # BuildMarine(location),
                    # BuildMarine(location),
                    # BuildMarine(location),
                    # BuildMarine(location),
                    # BuildMedivac(location),
                    # DumbAttack(location, 15, 47),
                    ResearchConcussiveShells(location),
                ]
            )
        ]
        for repeat in range(0, 100):
            for army in range(0, 2):
                goals = goals + [
                    OrderedGoal(
                        [
                            BuildSupplyDepot(location),
                            BuildMarine(location),
                            BuildMarine(location),
                            BuildMarine(location),
                            BuildMarine(location),
                            BuildMarine(location),
                            BuildMarine(location),
                            BuildMarine(location),
                            BuildMarauder(location),
                            BuildMarauder(location),
                            BuildMarauder(location),
                        ]
                    )
                ]
            # if repeat % 2 == 0:
            #target_x = 47
            #target_y = 47
            # else:
            #    target_x = 15
            #    target_y = 47
            for attack in range(0, 9):
                #orders = orders + [DumbAttack(location, target_x, target_y)]
                goals = goals + [AttackQuadrantGoal(self.attack_commander)]
        return goals

    def _goal_is_finished(self, observations: Observations) -> bool:
        return self.current_goal.done(observations)

    def _commander_name(self) -> str:
        return self.agent_name + "." + self.__class__.__name__

    def _extra_supply_depots(self, observations: Observations) -> Order:
        counter = BuildingCounter()
        expectMore = 8 > counter.supply_depots_count(observations)
        supplyAlmostFull = observations.player().food_cap() - observations.player().food_used() <= 2
        if expectMore and supplyAlmostFull:
            return BuildSupplyDepot(self.location)
        else:
            return NoOrder()


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


class AttackQuadrantGoal(Goal):

    def __init__(self, attack_commander: AttackCommander):
        self.attack_commander = attack_commander
        self.current_order = None

    def order(self, observations: Observations) -> SmartOrder:
        self.current_order = self.attack_commander.order(observations)
        return self.current_order

    def done(self, observations: Observations) -> bool:
        if not self.current_order:
            self.current_order = self.attack_commander.order(observations)
        return self.current_order.done(observations)
