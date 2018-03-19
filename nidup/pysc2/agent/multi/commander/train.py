
import numpy as np
from nidup.pysc2.agent.commander import Commander
from nidup.pysc2.learning.qlearning import QLearningTable, QLearningTableStorage
from nidup.pysc2.agent.order import Order
from nidup.pysc2.agent.information import Location, BuildingCounter, EnemyDetector, RaceNames,EpisodeDetails
from nidup.pysc2.agent.multi.order.common import NoOrder
from nidup.pysc2.agent.multi.order.train import BuildMarine, BuildMarauder, BuildHellion, BuildMedivac
from nidup.pysc2.wrapper.observations import Observations

ACTION_DO_NOTHING = 'donothing'
ACTION_BUILD_MARINE = 'buildmarine'
ACTION_BUILD_MARAUDER = 'buildmarauder'
ACTION_BUILD_HELLION = 'buildhellion'
ACTION_BUILD_MEDIVAC = 'buildmedivac'


class TrainActions:

    def __init__(self, location: Location):
        self.location = location
        self.actions = [
            ACTION_DO_NOTHING,
            ACTION_BUILD_MARINE,
            ACTION_BUILD_MARAUDER,
            ACTION_BUILD_HELLION,
            ACTION_BUILD_MEDIVAC,
        ]

    def all(self) -> []:
        return self.actions

    def order(self, action_id: str) -> Order:
        smart_action = self.actions[action_id]
        if smart_action == ACTION_BUILD_MARINE:
            return BuildMarine(self.location)
        elif smart_action == ACTION_BUILD_MARAUDER:
            return BuildMarauder(self.location)
        elif smart_action == ACTION_BUILD_HELLION:
            return BuildHellion(self.location)
        elif smart_action == ACTION_BUILD_MEDIVAC:
            return BuildMedivac(self.location)
        elif smart_action == ACTION_DO_NOTHING:
            return NoOrder()
        else:
            raise Exception('The smart action ' + smart_action + " is unknown")


class TrainStateBuilder:

    def build_state(self, observations: Observations, enemy_detector: EnemyDetector) -> []:
        counter = BuildingCounter()

        base_state_items_length = 9

        # TODO can be simplified a lot if actions comes from BO, also means we split per BO
        current_state = np.zeros(base_state_items_length)
        current_state[0] = counter.command_center_count(observations)
        current_state[1] = counter.supply_depots_count(observations)
        current_state[2] = counter.barracks_count(observations)
        current_state[3] = counter.factories_count(observations)
        current_state[4] = counter.techlab_barracks_count(observations)
        current_state[5] = counter.reactor_barracks_count(observations)
        current_state[6] = counter.starports_count(observations)
        current_state[7] = self._enemy_race_id(enemy_detector)
        current_state[8] = observations.player().food_army()

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
        self.previous_action = None
        self.previous_state = None
        self.previous_order = None
        self.smart_actions = TrainActions(self.location)
        self.qlearn = QLearningTable(actions=list(range(len(self.smart_actions.all()))))
        QLearningTableStorage().load(self.qlearn, self._commander_name())
        self.last_played_step = 0
        self.number_steps_between_order = 10
        self.episode_details = episode_details

    def order(self, observations: Observations)-> Order:
        if observations.last():
            return NoOrder()
        if not self._can_play():
            return NoOrder()

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
            QLearningTableStorage().save(self.qlearn, self._commander_name())
            self.previous_action = None
            self.previous_state = None
            self.previous_order = None

    def _commander_name(self) -> str:
        return self.agent_name + "." + self.__class__.__name__

    def _update_last_played_step(self):
        self.last_played_step = self.episode_details.episode_step()

    def _can_play(self) -> bool:
        return self.last_played_step + self.number_steps_between_order < self.episode_details.episode_step()
