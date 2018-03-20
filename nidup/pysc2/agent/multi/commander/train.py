
import numpy as np
from nidup.pysc2.agent.commander import Commander
from nidup.pysc2.learning.qlearning import QLearningTable, QLearningTableStorage
from nidup.pysc2.agent.order import Order
from nidup.pysc2.agent.information import Location, EnemyDetector, RaceNames, EpisodeDetails
from nidup.pysc2.agent.multi.order.common import NoOrder
from nidup.pysc2.agent.multi.order.train import BuildMarine, BuildMarauder, BuildHellion, BuildMedivac
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.agent.multi.commander.build import OrderedBuildOrder
from nidup.pysc2.agent.multi.commander.common import TrainActionsCodes


class TrainActions:

    def __init__(self, location: Location, code: str, train_actions: []):
        self.location = location
        self.code_str = code
        self.actions = train_actions

    def all(self) -> []:
        return self.actions

    def order(self, action_id: str) -> Order:
        smart_action = self.actions[action_id]
        if smart_action == TrainActionsCodes().train_marine():
            return BuildMarine(self.location)
        elif smart_action == TrainActionsCodes().train_marauder():
            return BuildMarauder(self.location)
        elif smart_action == TrainActionsCodes().train_hellion():
            return BuildHellion(self.location)
        elif smart_action == TrainActionsCodes().train_medivac():
            return BuildMedivac(self.location)
        elif smart_action == TrainActionsCodes().do_nothing():
            return NoOrder()
        else:
            raise Exception('The smart action ' + smart_action + " is unknown")

    def code(self) -> str:
        return self.code_str


class TrainStateBuilder:

    def build_state(self, observations: Observations, enemy_detector: EnemyDetector) -> []:
        base_state_items_length = 2
        current_state = np.zeros(base_state_items_length)
        current_state[0] = self._enemy_race_id(enemy_detector)
        current_state[1] = observations.player().food_army()

        return current_state

    def _enemy_race_id(self, enemy_detector: EnemyDetector) -> int:
        race = enemy_detector.race()
        name_to_id = {
            RaceNames().unknown(): 0,
            RaceNames().protoss(): 1,
            RaceNames().terran(): 2,
            RaceNames().zerg(): 3,
        }
        return name_to_id[race]


class TrainingCommander(Commander):

    def __init__(self, location: Location, agent_name: str, enemy_detector: EnemyDetector, episode_details: EpisodeDetails):
        super(Commander, self).__init__()
        self.location = location
        self.agent_name = agent_name
        self.enemy_detector = enemy_detector
        self.smart_actions = None
        self.qlearn = None
        self.previous_action = None
        self.previous_state = None
        self.previous_order = None
        self.build_orders = None
        self.last_played_step = 0
        self.number_steps_between_order = 10
        self.episode_details = episode_details

    def order(self, observations: Observations)-> Order:
        if observations.last():
            return NoOrder()
        if not self._can_play():
            return NoOrder()

        if not self.qlearn:
            self.smart_actions = TrainActions(
                self.location, self.build_orders.name(), self.build_orders.training_actions_set().actions()
            )
            self.qlearn = QLearningTable(actions=list(range(len(self.smart_actions.all()))))
            QLearningTableStorage().load(self.qlearn, self._qlearning_name())

        if not self.previous_order or self.previous_order.done(observations) or isinstance(self.previous_order, NoOrder):
            current_state = TrainStateBuilder().build_state(observations, self.enemy_detector)
            if self.previous_action is not None:
                self.qlearn.learn(str(self.previous_state), self.previous_action, 0, str(current_state))
            rl_action = self.qlearn.choose_action(str(current_state))
            self.previous_state = current_state
            self.previous_action = rl_action
            self.previous_order = self.smart_actions.order(rl_action)
            print(rl_action)
            self._update_last_played_step()

        print(self.previous_order)

        return self.previous_order

    def learn_on_last_episode_step(self, observations: Observations):
        if self.previous_action:
            print("learn train terminal")
            print(str(self.previous_state))
            print(self.previous_action)
            self.qlearn.learn(str(self.previous_state), self.previous_action, observations.reward(), 'terminal')
            QLearningTableStorage().save(self.qlearn, self._qlearning_name())
            self.previous_action = None
            self.previous_state = None
            self.previous_order = None

    def configure_build_orders(self, build_orders: OrderedBuildOrder):
        self.build_orders = build_orders

    def current_build_orders(self) -> OrderedBuildOrder:
        return self.build_orders

    def _commander_name(self) -> str:
        return self.agent_name + "." + self.__class__.__name__

    def _qlearning_name(self) -> str:
        return self._commander_name() + "." + self.build_orders.training_actions_set().code()

    def _update_last_played_step(self):
        self.last_played_step = self.episode_details.episode_step()

    def _can_play(self) -> bool:
        return self.last_played_step + self.number_steps_between_order < self.episode_details.episode_step()
