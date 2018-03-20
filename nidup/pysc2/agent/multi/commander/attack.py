
import numpy as np
from nidup.pysc2.agent.commander import Commander
from nidup.pysc2.learning.qlearning import QLearningTable, QLearningTableStorage
from nidup.pysc2.agent.order import Order
from nidup.pysc2.agent.information import Location, MinimapEnemyHotSquaresBuilder, EnemyDetector, RaceNames
from nidup.pysc2.agent.multi.order.common import NoOrder
from nidup.pysc2.agent.multi.order.attack import QLearningAttack, QLearningAttackOffsetsProvider
from nidup.pysc2.wrapper.observations import Observations

ACTION_DO_NOTHING = 'donothing'
ACTION_ATTACK = 'attack'


class AttackActions:

    def __init__(self, location: Location, offsets_provider: QLearningAttackOffsetsProvider):
        self.location = location
        self.offsets_provider = offsets_provider
        self.actions = [
            ACTION_DO_NOTHING
        ]
        # split the mini-map into four quadrants keep the action space small to make it easier for the agent to learn
        attack_actions = []
        for mm_x in range(0, 64):
            for mm_y in range(0, 64):
                if (mm_x + 1) % 32 == 0 and (mm_y + 1) % 32 == 0:
                    attack_actions.append(ACTION_ATTACK + '_' + str(mm_x - 16) + '_' + str(mm_y - 16))
        # remove the player's base quadrant
        del attack_actions[0]
        # keep only enemy's base 1 and base 2 quadrants (natural expansion)
        del attack_actions[1]
        self.actions = self.actions + attack_actions

    def all(self) -> []:
        return self.actions

    def order(self, action_id: str) -> Order:
        smart_action, x, y = self._split_action(action_id)
        if smart_action == ACTION_ATTACK:
            return QLearningAttack(self.location, self.offsets_provider, int(x), int(y))
        elif smart_action == ACTION_DO_NOTHING:
            return NoOrder()
        else:
            raise Exception('The attack action ' + smart_action + " is unknown")

    def _split_action(self, action_id):
        smart_action = self.actions[action_id]
        x = 0
        y = 0
        if '_' in smart_action:
            smart_action, x, y = smart_action.split('_')
        return smart_action, x, y


class AttackStateBuilder:

    def build_state(self, location: Location, observations: Observations, enemy_detector: EnemyDetector) -> []:
        base_state_items_length = 2
        hot_squares_length = 4
        current_state_length = base_state_items_length + hot_squares_length

        current_state = np.zeros(current_state_length)
        current_state[0] = self._enemy_race_id(enemy_detector)
        current_state[1] = observations.player().food_army()

        hot_squares = MinimapEnemyHotSquaresBuilder().minimap_four_squares(observations, location)
        for i in range(0, hot_squares_length):
            current_state[i + base_state_items_length] = hot_squares[i]

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


class AttackCommander(Commander):

    def __init__(self, location: Location, agent_name: str, enemy_detector: EnemyDetector):
        super(Commander, self).__init__()
        self.location = location
        self.agent_name = agent_name
        self.enemy_detector = enemy_detector
        self.previous_action = None
        self.previous_state = None
        self.previous_order = None
        self.attack_offsets_provider = QLearningAttackOffsetsProvider(agent_name, location)
        self.smart_actions = AttackActions(self.location, self.attack_offsets_provider)
        self.qlearn = QLearningTable(actions=list(range(len(self.smart_actions.all()))))
        QLearningTableStorage().load(self.qlearn, self._commander_name())

    def order(self, observations: Observations)-> Order:
        if observations.last():
            return NoOrder()

        if not self.previous_order or self.previous_order.done(observations):
            current_state = AttackStateBuilder().build_state(self.location, observations, self.enemy_detector)
            if self.previous_action is not None:
                self.qlearn.learn(str(self.previous_state), self.previous_action, 0, str(current_state))
            rl_action = self.qlearn.choose_action(str(current_state))
            self.previous_state = current_state
            self.previous_action = rl_action
            self.previous_order = self.smart_actions.order(rl_action)

        return self.previous_order

    def learn_on_last_episode_step(self, observations: Observations):
        if self.previous_action:
            #print("learn attack terminal")
            #print(str(self.previous_state))
            #print(self.previous_action)
            self.qlearn.learn(str(self.previous_state), self.previous_action, observations.reward(), 'terminal')
            QLearningTableStorage().save(self.qlearn, self._commander_name())
            self.previous_action = None
            self.previous_state = None
            self.previous_order = None
            self.attack_offsets_provider.save_learning_at_the_end_of_an_episode()

    def _commander_name(self) -> str:
        return self.agent_name + "." + self.__class__.__name__
