
import numpy as np
from nidup.pysc2.agent.multi.info.enemy import EnemyRaceDetector, RaceNames
from nidup.pysc2.agent.multi.info.player import Location
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.agent.multi.goal.common import OrderedGoal
from nidup.pysc2.agent.multi.order.train import BuildMarine, BuildMarauder
from nidup.pysc2.learning.qlearning import QLearningTable, QLearningTableStorage


class TrainSquadGoal(OrderedGoal):

    def __init__(self, orders: []):
        OrderedGoal.__init__(self, orders)


class TrainSquadGoalFactory:

    def train_7marines_3marauders(self, location: Location) -> TrainSquadGoal:
        return TrainSquadGoal(
            [
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

    def train_5marines_5marauders(self, location: Location) -> TrainSquadGoal:
        return TrainSquadGoal(
            [
                BuildMarine(location),
                BuildMarine(location),
                BuildMarine(location),
                BuildMarine(location),
                BuildMarine(location),
                BuildMarauder(location),
                BuildMarauder(location),
                BuildMarauder(location),
                BuildMarauder(location),
                BuildMarauder(location),
            ]
        )

    def train_3marines_7marauders(self, location: Location) -> TrainSquadGoal:
        return TrainSquadGoal(
            [
                BuildMarine(location),
                BuildMarine(location),
                BuildMarine(location),
                BuildMarauder(location),
                BuildMarauder(location),
                BuildMarauder(location),
                BuildMarauder(location),
                BuildMarauder(location),
                BuildMarauder(location),
                BuildMarauder(location),
            ]
        )

    def train_10marines(self, location: Location) -> TrainSquadGoal:
        return TrainSquadGoal(
            [
                BuildMarine(location),
                BuildMarine(location),
                BuildMarine(location),
                BuildMarine(location),
                BuildMarine(location),
                BuildMarine(location),
                BuildMarine(location),
                BuildMarine(location),
                BuildMarine(location),
                BuildMarine(location),
            ]
        )


class TrainSquadActionsCodes:

    def train_7marines_3marauders(self) -> str:
        return 'train_7marines_3marauders'

    def train_5marines_5marauders(self) -> str:
        return 'train_5marines_5marauders'

    def train_3marines_7marauders(self) -> str:
        return 'train_3marines_7marauders'

    def train_10marines(self) -> str:
        return 'train_10marines'

    def all(self) -> []:
        return [
            self.train_7marines_3marauders(),
            self.train_5marines_5marauders(),
            self.train_3marines_7marauders(),
            self.train_10marines()
        ]


class TrainSquadActions:

    def __init__(self, location: Location, train_actions: []):
        self.location = location
        self.actions = train_actions

    def all(self) -> []:
        return self.actions

    def goal(self, action_id: str) -> TrainSquadGoal:
        smart_action = self.actions[action_id]
        if smart_action == TrainSquadActionsCodes().train_7marines_3marauders():
            return TrainSquadGoalFactory().train_7marines_3marauders(self.location)
        elif smart_action == TrainSquadActionsCodes().train_5marines_5marauders():
            return TrainSquadGoalFactory().train_5marines_5marauders(self.location)
        elif smart_action == TrainSquadActionsCodes().train_3marines_7marauders():
            return TrainSquadGoalFactory().train_3marines_7marauders(self.location)
        elif smart_action == TrainSquadActionsCodes().train_10marines():
            return TrainSquadGoalFactory().train_10marines(self.location)
        else:
            raise Exception('The smart action ' + smart_action + " is unknown")


class TrainStateBuilder:

    def build_state(self, enemy_detector: EnemyRaceDetector) -> []:
        base_state_items_length = 1
        current_state = np.zeros(base_state_items_length)
        current_state[0] = self._enemy_race_id(enemy_detector)

        return current_state

    def _enemy_race_id(self, enemy_detector: EnemyRaceDetector) -> int:
        race = enemy_detector.race()
        name_to_id = {
            RaceNames().unknown(): 0,
            RaceNames().protoss(): 1,
            RaceNames().terran(): 2,
            RaceNames().zerg(): 3,
        }
        return name_to_id[race]


class TrainSquadGoalProvider:

    def __init__(self, location: Location, agent_name: str, enemy_detector: EnemyRaceDetector):
        self.location = location
        self.agent_name = agent_name
        self.enemy_detector = enemy_detector
        self.smart_actions = None
        self.qlearn = None
        self.previous_action = None
        self.previous_state = None

    def goal(self, observations: Observations)-> TrainSquadGoal:
        if not self.qlearn:
            self.smart_actions = TrainSquadActions(self.location, TrainSquadActionsCodes().all())
            self.qlearn = QLearningTable(actions=list(range(len(self.smart_actions.all()))))
            QLearningTableStorage().load(self.qlearn, self._qlearning_name())

        current_state = TrainStateBuilder().build_state(self.enemy_detector)
        if self.previous_action is not None:
            self.qlearn.learn(str(self.previous_state), self.previous_action, 0, str(current_state))
        rl_action = self.qlearn.choose_action(str(current_state))
        print("train squad action,race," + str(rl_action) + "," + self.enemy_detector.race())
        self.previous_state = current_state
        self.previous_action = rl_action
        return self.smart_actions.goal(rl_action)

    def learn_on_last_episode_step(self, observations: Observations):
        if self.previous_action:
            self.qlearn.learn(str(self.previous_state), self.previous_action, observations.reward(), 'terminal')
            QLearningTableStorage().save(self.qlearn, self._qlearning_name())
            self.previous_action = None
            self.previous_state = None

    def _qlearning_name(self) -> str:
        return self.agent_name + "." + self.__class__.__name__
