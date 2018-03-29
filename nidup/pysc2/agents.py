
# common
import time
from pysc2.agents.base_agent import BaseAgent
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.learning.game_results import GameResultsTable, FinishedGameInformationDetails
# multi
import nidup.pysc2.agent.multi as multi
from nidup.pysc2.agent.multi.commander.main import MultiGameCommander
# hybrid
import nidup.pysc2.agent.hybrid as hybrid
from nidup.pysc2.agent.hybrid.commander import HybridGameCommander
# smart
from nidup.pysc2.agent.smart.commander import QLearningCommander
# scripted
import nidup.pysc2.agent.scripted as scripted
from nidup.pysc2.agent.scripted.commander import GameCommander, ScoutingCommander, NoOrder
from nidup.pysc2.agent.hybrid.orders import PrepareSCVControlGroupsOrder, BuildRefinery, FillRefineryOnceBuilt, BuildSCV
from nidup.pysc2.agent.multi.order.build import BuildSupplyDepot
from nidup.pysc2.agent.multi.order.common import NoOrder


# Generation 3 - expecting good win ratio against medium built-in AI
class MultiReinforcementAgent(BaseAgent):

    def __init__(self):
        super(MultiReinforcementAgent, self).__init__()
        self.commander = None
        self.enemy_race_detector = None
        self.enemy_units_detector = None
        self.episode_details = None

    def step(self, obs):
        super(MultiReinforcementAgent, self).step(obs)
        observations = Observations(obs)
        if observations.first():
            base_location = multi.info.player.Location(observations)
            self.enemy_race_detector = multi.info.enemy.EnemyRaceDetector()
            self.enemy_units_detector = multi.info.enemy.EnemyUnitsDetector()
            self.episode_details = multi.info.episode.EpisodeDetails()
            self.commander = MultiGameCommander(base_location, self.name(), self.enemy_race_detector, self.episode_details)
        elif observations.last():
            self.commander.learn_on_last_episode_step(observations)
            game_results = GameResultsTable(self.name())
            game_info = FinishedGameInformationDetails(
                self.episode_details.episode_step(),
                self.enemy_race_detector.race(),
                "HardCoded",#self.commander.build_order_commander.current_build_orders().name()
                ", ".join(str(unit_id) for unit_id in self.enemy_units_detector.detected_units().all())
            )
            game_results.append(observations.reward(), observations.score_cumulative(), game_info)
        self.episode_details.increment_episode_step()
        self.enemy_units_detector.detect_units(observations)
        return self.commander.order(observations).execute(observations)

    def name(self) -> str:
        return __name__ + "." + self.__class__.__name__


# Generation 2 - good win ratio against easy built-in AI
class HybridAttackReinforcementAgent(BaseAgent):

    def __init__(self):
        super(HybridAttackReinforcementAgent, self).__init__()
        self.commander = None
        self.enemy_detector = None
        self.episode_details = None

    def step(self, obs):
        super(HybridAttackReinforcementAgent, self).step(obs)
        observations = Observations(obs)
        if observations.first():
            base_location = hybrid.information.Location(observations)
            self.enemy_detector = hybrid.information.EnemyDetector()
            self.episode_details = hybrid.information.EpisodeDetails()
            self.commander = HybridGameCommander(base_location, self.name(), self.enemy_detector, self.episode_details)
        elif observations.last():
            game_results = GameResultsTable(self.name())
            game_info = FinishedGameInformationDetails(0, self.enemy_detector.race(), "unknown", "unknown")
            game_results.append(observations.reward(), observations.score_cumulative(), game_info)
        self.episode_details.increment_episode_step()
        return self.commander.order(observations).execute(observations)

    def name(self) -> str:
        return __name__ + "." + self.__class__.__name__


# Generation 1 - good win ratio against very-easy built-in AI
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
            game_info = FinishedGameInformationDetails(0, "unknown", "unknown", "unknown")
            game_results.append(observations.reward(), observations.score_cumulative(), game_info)

        return self.commander.order(observations).execute(observations)

    def name(self) -> str:
        return __name__ + "." + self.__class__.__name__


# Scripted agent
class BuildOrderAgent(BaseAgent):

    commander = None
    debug = False

    def step(self, obs):
        super(BuildOrderAgent, self).step(obs)
        observations = Observations(obs)
        if observations.first():
            base_location = scripted.information.Location(observations)
            self.commander = GameCommander(base_location)
        elif observations.last():
            game_results = GameResultsTable(self.name())
            game_info = FinishedGameInformationDetails(0, "unknown", "unknown", "unknown")
            game_results.append(observations.reward(), observations.score_cumulative(), game_info)
        if self.debug:
            time.sleep(0.5)
        return self.commander.order(observations).execute(observations)

    def name(self) -> str:
        return __name__ + "." + self.__class__.__name__


# Scripted agent
class ScoutingAgent(BaseAgent):

    commander = None
    infinite_scouting = True

    def step(self, obs):
        super(ScoutingAgent, self).step(obs)
        observations = Observations(obs)
        if observations.first():
            base_location = scripted.information.Location(observations)
            self.commander = ScoutingCommander(base_location, self.infinite_scouting)
        return self.commander.order(observations).execute(observations)


# Scripted agent
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
            self.base_location = scripted.information.Location(observations)
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


# Scripted agent
class SCVControlGroupsAgent(BaseAgent):

    def __init__(self):
        BaseAgent.__init__(self)
        self.base_location = None
        self.order = None

    def step(self, obs):
        super(SCVControlGroupsAgent, self).step(obs)
        observations = Observations(obs)
        if observations.first():
            self.base_location = scripted.information.Location(observations)
            self.order = PrepareSCVControlGroupsOrder(self.base_location)
        print(observations.control_groups())
        return self.order.execute(observations)


# Scripted agent
class SupplyDepotsAgent(BaseAgent):

    def __init__(self):
        BaseAgent.__init__(self)
        self.base_location = None
        self.group_order = None
        self.supply_depots_orders = None
        self.supply_depot_order = None

    def step(self, obs):
        super(SupplyDepotsAgent, self).step(obs)
        observations = Observations(obs)
        if observations.first():
            self.base_location = scripted.information.Location(observations)
            self.group_order = PrepareSCVControlGroupsOrder(self.base_location)
        if not self.group_order.done(observations):
            return self.group_order.execute(observations)

        if not self.supply_depots_orders:
            self.supply_depots_orders = []
            for i in range(0, 9):
                self.supply_depots_orders.append(BuildSupplyDepot(self.base_location))
            self.supply_depot_order = self.supply_depots_orders.pop(0)
        if self.supply_depot_order.done(observations) and len(self.supply_depots_orders) > 0:
            self.supply_depot_order = self.supply_depots_orders.pop(0)
        if not self.supply_depot_order.done(observations):
            return self.supply_depot_order.execute(observations)
        return NoOrder().execute(observations)
