
import time
from pysc2.agents.base_agent import BaseAgent
from nidup.pysc2.agent.scripted.commander import GameCommander, ScoutingCommander, NoOrder
from nidup.pysc2.agent.information import Location, EnemyDetector
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.learning.game_results import GameResultsTable, FinishedGameInformationDetails
from nidup.pysc2.agent.smart.commander import QLearningCommander
from nidup.pysc2.agent.hybrid.commander import HybridGameCommander
from nidup.pysc2.agent.smart.orders import PrepareSCVControlGroupsOrder, BuildRefinery, FillRefineryOnceBuilt, BuildSCV


class HybridAttackReinforcementAgent(BaseAgent):

    def __init__(self):
        super(HybridAttackReinforcementAgent, self).__init__()
        self.commander = None
        self.enemy_detector = None

    def step(self, obs):
        super(HybridAttackReinforcementAgent, self).step(obs)
        observations = Observations(obs)
        if observations.first():
            base_location = Location(observations)
            self.enemy_detector = EnemyDetector()
            self.commander = HybridGameCommander(base_location, self.name(), self.enemy_detector)
        elif observations.last():
            game_results = GameResultsTable(self.name())
            game_info = FinishedGameInformationDetails(self.steps, self.enemy_detector.race())
            game_results.append(observations.reward(), observations.score_cumulative(), game_info)
        return self.commander.order(observations, self.steps).execute(observations)

    def name(self) -> str:
        return __name__ + "." + self.__class__.__name__


class ReinforcementMarineAgent(BaseAgent):

    def __init__(self):
        super(ReinforcementMarineAgent, self).__init__()
        self.commander = None

    def step(self, obs):
        super(ReinforcementMarineAgent, self).step(obs)
        observations = Observations(obs)
        if observations.first():
            self.commander = QLearningCommander(self.name())
        elif observations.last():
            game_results = GameResultsTable(self.name())
            game_info = FinishedGameInformationDetails(self.steps, "unknown")
            game_results.append(observations.reward(), observations.score_cumulative(), game_info)

        return self.commander.order(observations, self.steps).execute(observations)

    def name(self) -> str:
        return __name__ + "." + self.__class__.__name__


class BuildOrderAgent(BaseAgent):

    commander = None
    debug = False

    def step(self, obs):
        super(BuildOrderAgent, self).step(obs)
        observations = Observations(obs)
        if observations.first():
            base_location = Location(observations)
            self.commander = GameCommander(base_location)
        elif observations.last():
            game_results = GameResultsTable(self.name())
            game_info = FinishedGameInformationDetails(self.steps, "unknown")
            game_results.append(observations.reward(), observations.score_cumulative(), game_info)
        if self.debug:
            time.sleep(0.5)
        return self.commander.order(observations, self.steps).execute(observations)

    def name(self) -> str:
        return __name__ + "." + self.__class__.__name__


class ScoutingAgent(BaseAgent):

    commander = None
    infinite_scouting = True

    def step(self, obs):
        super(ScoutingAgent, self).step(obs)
        observations = Observations(obs)
        if observations.first():
            base_location = Location(observations)
            self.commander = ScoutingCommander(base_location, self.infinite_scouting)
        return self.commander.order(observations, self.steps).execute(observations)


class SCVHarvesterAgent(BaseAgent):

    debug = False

    def __init__(self):
        BaseAgent.__init__(self)
        self.base_location = None
        self.control_group_order = None
        self.order_first_refinery = None
        self.order_second_refinery = None
        self.fill_refinery_one_order = None
        self.fill_refinery_second_order = None
        self.train_scv_order = None

    def step(self, obs):
        super(SCVHarvesterAgent, self).step(obs)
        observations = Observations(obs)
        if observations.first():
            self.base_location = Location(observations)
            self.control_group_order = PrepareSCVControlGroupsOrder(self.base_location)
            self.order_first_refinery = BuildRefinery(self.base_location, 1)
            self.order_second_refinery = BuildRefinery(self.base_location, 2)
            self.fill_refinery_one_order = FillRefineryOnceBuilt(self.base_location, 1)
            self.fill_refinery_second_order = FillRefineryOnceBuilt(self.base_location, 2)
            self.train_scv_order = BuildSCV(self.base_location)
        if not self.control_group_order.done(observations):
            action = self.control_group_order.execute(observations)
        elif not self.order_first_refinery.done(observations):
            action = self.order_first_refinery.execute(observations)
        elif not self.order_second_refinery.done(observations):
            action = self.order_second_refinery.execute(observations)
        elif self.fill_refinery_one_order.doable(observations) and not self.fill_refinery_one_order.done(observations):
            action = self.fill_refinery_one_order.execute(observations)
        elif self.fill_refinery_second_order.doable(observations) and not self.fill_refinery_second_order.done(observations):
            action = self.fill_refinery_second_order.execute(observations)
        elif self.train_scv_order.doable(observations) and not self.train_scv_order.done(observations):
            action = self.train_scv_order.execute(observations)
        elif self.train_scv_order.doable(observations) and self.train_scv_order.done(observations):
            self.train_scv_order = BuildSCV(self.base_location)
            action = self.train_scv_order.execute(observations)
        else:
            action = NoOrder().execute(observations)
        if self.debug:
            time.sleep(0.5)
        return action


class SCVControlGroupsAgent(BaseAgent):

    def __init__(self):
        BaseAgent.__init__(self)
        self.base_location = None
        self.order = None

    def step(self, obs):
        super(SCVControlGroupsAgent, self).step(obs)
        observations = Observations(obs)
        if observations.first():
            self.base_location = Location(observations)
            self.order = PrepareSCVControlGroupsOrder(self.base_location)
        print(observations.control_groups())
        return self.order.execute(observations)
