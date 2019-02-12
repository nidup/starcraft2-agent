
import math
import random
import numpy as np
from nidup.pysc2.agent.commander import Commander
from nidup.pysc2.learning.qlearning import QLearningTable, QLearningTableStorage
from nidup.pysc2.agent.order import Order
from nidup.pysc2.agent.multi.info.enemy import EnemyRaceDetector, RaceNames
from nidup.pysc2.agent.multi.info.player import Location
from nidup.pysc2.agent.multi.order.common import NoOrder, SmartOrder
from nidup.pysc2.agent.multi.order.attack import SeekAndDestroyBuildingAttack, SeekAndDestroyAllUnitsAttack
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.agent.multi.info.minimap import MinimapQuadrant, MinimapAnalyser

ACTION_DO_NOTHING = 'donothing'
ACTION_ATTACK = 'attack'
_PLAYER_ENEMY = 4


class NormalizedMinimapTargetToMinimapQuadrant:

    def quadrant(self, location: Location, minimap_target: []) -> MinimapQuadrant:
        minimap_quadrant_index = None
        if minimap_target == [47, 47]:
            minimap_quadrant_index = 4 if location.base_top_left else 1
        elif minimap_target == [15, 47]:
            minimap_quadrant_index = 3 if location.base_top_left else 2
        elif minimap_target == [47, 15]:
            minimap_quadrant_index = 2 if location.base_top_left else 3
        elif minimap_target == [15, 15]:
            minimap_quadrant_index = 1 if location.base_top_left else 4
        return MinimapQuadrant(minimap_quadrant_index)


class AttackActions:

    # ['donothing', 'attack_15_47', 'attack_15_47', 'attack_47_15', 'attack_47_47']
    def __init__(self, location: Location):
        self.location = location
        self.actions = [
            ACTION_DO_NOTHING
        ]
        # split the mini-map into four quadrants keep the action space small to make it easier for the agent to learn
        attack_actions = []
        for mm_x in range(0, 64):
            for mm_y in range(0, 64):
                if (mm_x + 1) % 32 == 0 and (mm_y + 1) % 32 == 0:
                    attack_actions.append(ACTION_ATTACK + '_' + str(mm_x - 16) + '_' + str(mm_y - 16))
        self.actions = self.actions + attack_actions

    def all(self) -> []:
        return self.actions

    def order(self, action_id: str) -> Order:
        smart_action, x, y = self._split_action(action_id)
        if smart_action == ACTION_ATTACK:
            quadrant = NormalizedMinimapTargetToMinimapQuadrant().quadrant(self.location, [int(x), int(y)])
            return SeekAndDestroyBuildingAttack(self.location, quadrant)
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

    def build_state(self, location: Location, observations: Observations, enemy_detector: EnemyRaceDetector) -> []:
        base_state_items_length = 2
        hot_squares_length = 4
        current_state_length = base_state_items_length + hot_squares_length

        current_state = np.zeros(current_state_length)
        current_state[0] = self._enemy_race_id(enemy_detector)
        current_state[1] = self._simplified_army_size(observations)

        hot_squares = self._enemy_buildings_on_minimap_quadrants(location, observations)
        for i in range(0, hot_squares_length):
            current_state[i + base_state_items_length] = hot_squares[i]

        return current_state

    # different learning per race
    def _enemy_race_id(self, enemy_detector: EnemyRaceDetector) -> int:
        race = enemy_detector.race()
        name_to_id = {
            RaceNames().unknown(): 0,
            RaceNames().protoss(): 1,
            RaceNames().terran(): 2,
            RaceNames().zerg(): 3,
        }
        return name_to_id[race]

    # from 0 to 200 to 0 to 40 in order to accelerate the learning
    def _simplified_army_size(self, observations: Observations):
        food_army = observations.player().food_army()
        army_size = 0
        if food_army > 0:
            army_size = food_army / 5
            army_size = math.floor(army_size)
        return army_size

    # return [0, 1, 0, 0] with 1 when buildings is present, 0 if no (normalized to have the same value when playing
    # top left or bottom right)
    def _enemy_buildings_on_minimap_quadrants(self, location: Location, observations: Observations) -> []:
        analyse = MinimapAnalyser().analyse(observations)
        hot_squares = np.zeros(4)
        if len(analyse.enemy_buildings_positions().positions(MinimapQuadrant(1))) > 0:
            hot_squares[0] = 1
        if len(analyse.enemy_buildings_positions().positions(MinimapQuadrant(2))) > 0:
            hot_squares[1] = 1
        if len(analyse.enemy_buildings_positions().positions(MinimapQuadrant(3))) > 0:
            hot_squares[2] = 1
        if len(analyse.enemy_buildings_positions().positions(MinimapQuadrant(4))) > 0:
            hot_squares[3] = 1
        if not location.command_center_is_top_left():
            hot_squares = hot_squares[::-1]
        return hot_squares


# commander acting in early and mid game, using QLearning approach to know which minimap quadrant it should attack
class AttackCommander(Commander):

    def __init__(self, location: Location, agent_name: str, enemy_detector: EnemyRaceDetector):
        super(Commander, self).__init__()
        self.location = location
        self.agent_name = agent_name
        self.enemy_detector = enemy_detector
        self.previous_action = None
        self.previous_state = None
        self.previous_order = None
        self.smart_actions = AttackActions(self.location)
        self.qlearn = QLearningTable(actions=list(range(len(self.smart_actions.all()))))
        QLearningTableStorage().load(self.qlearn, self._commander_name())

    def order(self, observations: Observations)-> Order:
        if observations.last():
            return NoOrder()

        if not self.previous_order or self.previous_order.done(observations):
            current_state = AttackStateBuilder().build_state(self.location, observations, self.enemy_detector)
            if self.previous_action is not None:
                reward = 0
                self.qlearn.learn(str(self.previous_state), self.previous_action, reward, str(current_state))
            rl_action = self.qlearn.choose_action(str(current_state))
            self.previous_state = current_state
            self.previous_action = rl_action
            self.previous_order = self.smart_actions.order(rl_action)

        return self.previous_order

    def learn_on_last_episode_step(self, observations: Observations):
        if self.previous_action:
            self.qlearn.learn(str(self.previous_state), self.previous_action, observations.reward(), 'terminal')
            QLearningTableStorage().save(self.qlearn, self._commander_name())
            self.previous_action = None
            self.previous_state = None
            self.previous_order = None

    def _commander_name(self) -> str:
        return self.agent_name + "." + self.__class__.__name__


# commander acting in late game, when no more mineral to collect, allowing to seek and destroy remaining enemies
class LateGameAttackCommander(Commander):

    def __init__(self, location: Location):
        super(Commander, self).__init__()
        self.location = location

    def order(self, observations: Observations)-> Order:
        return self._seek_and_destroy_orders(observations)

    def _seek_and_destroy_orders(self, observations: Observations) -> SmartOrder:
        print("seek and destroy order - late game")
        map_analyse = MinimapAnalyser().analyse(observations)
        quadrants = [MinimapQuadrant(1), MinimapQuadrant(2), MinimapQuadrant(3), MinimapQuadrant(4)]

        # start by the most probable enemy's base depending on player's base location
        if self.location.command_center_is_top_left():
            quadrants = quadrants[::-1]

        # seek and destroy buildings if there are
        for quadrant in quadrants:
            buildings = map_analyse.enemy_buildings_positions().positions(quadrant)
            if len(buildings) > 0:
                return SeekAndDestroyBuildingAttack(self.location, quadrant)

        # seek and destroy single units if there are
        for quadrant in quadrants:
            units = map_analyse.all_enemy_positions().positions(quadrant)
            if len(units) > 0:
                return SeekAndDestroyAllUnitsAttack(self.location, quadrant)

        # attack randomly, one after the other
        index = random.randint(0, len(quadrants) - 1)
        print("nothing on minimap, attack randomly the quadrant number "+str(index+1))
        return SeekAndDestroyBuildingAttack(self.location, quadrants[index])
