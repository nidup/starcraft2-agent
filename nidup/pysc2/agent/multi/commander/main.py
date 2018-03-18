
from nidup.pysc2.agent.commander import Commander
from nidup.pysc2.agent.order import Order
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.agent.information import Location, EnemyDetector, EpisodeDetails
from nidup.pysc2.agent.multi.order.common import NoOrder
from nidup.pysc2.agent.multi.commander.worker import WorkerCommander
from nidup.pysc2.agent.multi.commander.scout import ScoutCommander
from nidup.pysc2.agent.multi.commander.army import QLearningAttackCommander
from nidup.pysc2.agent.multi.commander.build import BuildOrderCommander

_PLAYER_ENEMY = 4


class MultiGameCommander(Commander):

    def __init__(self, base_location: Location, agent_name: str, enemy_detector: EnemyDetector, episode_details: EpisodeDetails):
        Commander.__init__(self)
        self.worker_commander = WorkerCommander(base_location, episode_details)
        self.enemy_detector = enemy_detector
        self.episode_details = episode_details
        self.scout_commander = ScoutCommander(base_location, self.enemy_detector)
        self.build_order_commander = BuildOrderCommander(base_location, agent_name, self.enemy_detector)
        self.attack_commander = QLearningAttackCommander(base_location, agent_name, self.enemy_detector)
        self.current_order = None
        self.enemy_detector = enemy_detector

    def order(self, observations: Observations)-> Order:

        if not self.current_order:
            self.current_order = self.worker_commander.order(observations)

        elif observations.last():
            self.attack_commander.learn_on_last_episode_step(observations)
            return NoOrder()

        elif self.current_order.done(observations):

            self.current_order = self.scout_commander.order(observations)
            if not isinstance(self.current_order, NoOrder):
                return self.current_order

            self.current_order = self.worker_commander.order(observations)
            if not isinstance(self.current_order, NoOrder):
                return self.current_order

            self.current_order = self.build_order_commander.order(observations)
            if not isinstance(self.current_order, NoOrder):
                return self.current_order

            # wait for the former build order to be finished
            if self.build_order_commander.build_is_finished(observations):
                self.current_order = self.attack_commander.order(observations)
            else:
                return self.current_order

        return self.current_order
