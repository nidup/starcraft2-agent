
import numpy as np
import random
from pysc2.lib import actions
from nidup.pysc2.agent.multi.order.common import SmartOrder
from nidup.pysc2.agent.information import Location
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.wrapper.actions import ActionQueueParameter
from nidup.pysc2.learning.qlearning import QLearningTable, QLearningTableStorage
from nidup.pysc2.agent.multi.minimap.analyser import MinimapAnalyser, MinimapQuadrant

_PLAYER_ENEMY = 4


class DumbAttack(SmartOrder):

    def __init__(self, location: Location, x: int , y: int):
        SmartOrder.__init__(self, location)
        self.step = 0
        self.x = x
        self.y = y

    def doable(self, observations: Observations) -> bool:
        return True

    def done(self, observations: Observations) -> bool:
        return self.step == 2

    def execute(self, observations: Observations) -> actions.FunctionCall:
        self.step = self.step + 1
        if self.step == 1:
            return self.select_army(observations)
        elif self.step == 2:
            return self.attack_minimap(observations)

    def select_army(self, observations: Observations) -> actions.FunctionCall:
        if self.action_ids.select_army() in observations.available_actions():
            return self.actions.select_army()

        return self.actions.no_op()

    def attack_minimap(self, observations: Observations) -> actions.FunctionCall:
        do_it = True
        if not observations.single_select().empty() and observations.single_select().unit_type() == self.unit_type_ids.terran_scv():
            do_it = False
        if not observations.multi_select().empty() and observations.multi_select().unit_type(0) == self.unit_type_ids.terran_scv():
            do_it = False

        if do_it and self.action_ids.attack_minimap() in observations.available_actions():
            x_offset = random.randint(-1, 1)
            y_offset = random.randint(-1, 1)
            target = self.location.transform_location(int(self.x) + (x_offset * 8), int(self.y) + (y_offset * 8))

            return self.actions.attack_minimap(target)

        return self.actions.no_op()


# Provides offset to attack into a quadrant, the same instance is injected into any QLearningAttack instances
class QLearningAttackOffsetsProvider:

    def __init__(self, agent_name: str, location: Location):
        self.agent_name = agent_name
        self.location = location
        self.actions = SmartAttackOffsetsActions()
        self.qlearn = QLearningTable(actions=list(range(len(self.actions.all()))))
        QLearningTableStorage().load(self.qlearn, self._qlearning_file_name())
        self.previous_action = None
        self.previous_state = None
        self.previous_killed_unit_score = 0
        self.previous_killed_building_score = 0

    def offsets(self, observations: Observations, minimap_target: []) -> []:

        current_state = AttackQuadrantStateBuilder().build_state(observations, self.location, minimap_target)
        killed_unit_score = observations.score_cumulative().killed_value_units()
        killed_building_score = observations.score_cumulative().killed_value_units()

        # reward inspired by https://chatbotslife.com/building-a-smart-pysc2-agent-cdc269cb095d
        if self.previous_action is not None:
            reward = 0
            if killed_unit_score > self.previous_killed_unit_score:
                reward += 0.1
            if killed_building_score > self.previous_killed_building_score:
                reward += 0.8
            self.qlearn.learn(str(self.previous_state), self.previous_action, reward, str(current_state))

        rl_action_id = self.qlearn.choose_action(str(current_state))
        self.previous_state = current_state
        self.previous_action = rl_action_id
        self.previous_killed_unit_score = killed_unit_score
        self.previous_killed_building_score = killed_building_score

        return self.actions.offsets(rl_action_id)

    def save_learning_at_the_end_of_an_episode(self):
        if self.previous_action:
            print("learn attack terminal order")
            print(str(self.previous_state))
            print(self.previous_action)
            QLearningTableStorage().save(self.qlearn, self._qlearning_file_name())

    def _qlearning_file_name(self) -> str:
        return self.agent_name + "." + self.__class__.__name__


class QLearningAttack(SmartOrder):

    def __init__(self, location: Location, offsets_provider: QLearningAttackOffsetsProvider, x: int, y: int):
        SmartOrder.__init__(self, location)
        self.step = 0
        self.offsets_provider = offsets_provider
        self.x = x
        self.y = y

    def doable(self, observations: Observations) -> bool:
        return True

    def done(self, observations: Observations) -> bool:
        return self.step == 2

    def execute(self, observations: Observations) -> actions.FunctionCall:
        self.step = self.step + 1
        if self.step == 1:
            return self.select_army(observations)
        elif self.step == 2:
            return self.attack_minimap(observations)

    def select_army(self, observations: Observations) -> actions.FunctionCall:
        if self.action_ids.select_army() in observations.available_actions():
            return self.actions.select_army()

        return self.actions.no_op()

    def attack_minimap(self, observations: Observations) -> actions.FunctionCall:
        do_it = True
        if not observations.single_select().empty() and observations.single_select().unit_type() == self.unit_type_ids.terran_scv():
            do_it = False
        if not observations.multi_select().empty() and observations.multi_select().unit_type(0) == self.unit_type_ids.terran_scv():
            do_it = False

        if do_it and self.action_ids.attack_minimap() in observations.available_actions():
            x_offset, y_offset = self.offsets_provider.offsets(observations, [self.x, self.y])
            target = self.location.transform_location(int(self.x) + (x_offset * 8), int(self.y) + (y_offset * 8))

            return self.actions.attack_minimap(target)

        return self.actions.no_op()


# Design attack actions on a game quadrant, ie, a potential base location (cf army_learning to understand the split
# into 4 quadrants. It defines 9 attacks offset positions applicable on any quadrant
class SmartAttackOffsetsActions:

    def __init__(self):
        self.actions = []

        for mm_x in range(3):
            for mm_y in range(3):
                self.actions.append(str(mm_x - 1) + '_' + str(mm_y - 1))

    def all(self) -> []:
        return self.actions

    def offsets(self, action_id: str) -> []:
        x, y = self._split_offset_action(action_id)
        return [int(x), int(y)]

    def _split_offset_action(self, action_id):
        x_offset, y_offset = self.actions[action_id].split('_')
        return x_offset, y_offset


# Design the attack quadrant state, from the center of one of the 4 attack quadrant, define 4 neighbours sections,
# each section represents 8x8 camera's section containing 1 if there is enemy, 0 if not.
class AttackQuadrantStateBuilder:

    def build_state(self, observations: Observations, location: Location, minimap_target: []) -> []:
        return MinimapQuadrantEnemyDetector().hot_sections(observations, location, minimap_target)


class MinimapQuadrantEnemyDetector:

    # returns 4 sections, marked as 1 if enemy are present, 0 if not
    def hot_sections(self, observations: Observations, location: Location, minimap_target: []):
        hot_sections = np.zeros(4)
        enemy_quadrant_y, enemy_quadrant_x = self._normalize_enemy_in_target_quadrant(observations, location, minimap_target)
        minimap_x, minimap_y = minimap_target
        for i in range(0, len(enemy_quadrant_y)):
            if enemy_quadrant_x[i] <= minimap_x and enemy_quadrant_y[i] <= minimap_y:
                hot_sections[0] = 1
            elif enemy_quadrant_x[i] >= minimap_x and enemy_quadrant_y[i] <= minimap_y:
                hot_sections[1] = 1
            elif enemy_quadrant_x[i] <= minimap_x and enemy_quadrant_y[i] >= minimap_y:
                hot_sections[2] = 1
            elif enemy_quadrant_x[i] >= minimap_x and enemy_quadrant_y[i] >= minimap_y:
                hot_sections[3] = 1
        #print(hot_sections)

        return hot_sections

    # filters enemies visible on the the minimap in the targeted 32x32 game quadrant
    def _normalize_enemy_in_target_quadrant(self, observations: Observations, location: Location, minimap_target: []):
        enemy_y, enemy_x = (observations.minimap().player_relative() == _PLAYER_ENEMY).nonzero()
        if enemy_y.any:

            # print("state")
            # print(minimap_target)
            # print(enemy_x)
            # print(enemy_y)

            minimap_x, minimap_y = minimap_target
            quadrant_enemy_x = []
            quadrant_enemy_y = []
            min_minimap_x = minimap_x - 16
            max_minimap_x = minimap_x + 16
            min_minimap_y = minimap_y - 16
            max_minimap_y = minimap_y + 16
            for i in range(0, len(enemy_y)):
                # reverse coordinate as we play the same way when starting from top-left or from bottom-down
                normed_enemy_x, normed_enemy_y = location.transform_location(enemy_x[i], enemy_y[i])
                in_x_section = min_minimap_x <= normed_enemy_x and normed_enemy_x <= max_minimap_x
                in_y_section = min_minimap_y <= normed_enemy_y and normed_enemy_y <= max_minimap_y
                if in_x_section and in_y_section:
                    quadrant_enemy_x.append(normed_enemy_x)
                    quadrant_enemy_y.append(normed_enemy_y)

            # print(quadrant_enemy_y)
            # print(quadrant_enemy_x)

            return quadrant_enemy_y, quadrant_enemy_x


class SeekAndDestroyAttack(SmartOrder):

    def __init__(self, location: Location, x: int, y: int):
        SmartOrder.__init__(self, location)
        self.step = 0
        self.x = x
        self.y = y

    def doable(self, observations: Observations) -> bool:
        return True

    def done(self, observations: Observations) -> bool:
        return self.step == 2

    def execute(self, observations: Observations) -> actions.FunctionCall:
        self.step = self.step + 1
        if self.step == 1:
            return self.select_army(observations)
        elif self.step >= 2:
            return self.attack_minimap(observations)

    def select_army(self, observations: Observations) -> actions.FunctionCall:
        if self.action_ids.select_army() in observations.available_actions():
            return self.actions.select_army()

        return self.actions.no_op()

    def attack_minimap(self, observations: Observations) -> actions.FunctionCall:
        do_it = True
        if not observations.single_select().empty() and observations.single_select().unit_type() == self.unit_type_ids.terran_scv():
            do_it = False
        if not observations.multi_select().empty() and observations.multi_select().unit_type(0) == self.unit_type_ids.terran_scv():
            do_it = False

        if do_it and self.action_ids.attack_minimap() in observations.available_actions():

            minimap_target = [self.x, self.y]

            enemy_base = None
            minimap_quadrant = None
            if minimap_target == [47, 47]:
                enemy_base = 1
                minimap_quadrant = 4 if self.location.base_top_left else 1
            elif minimap_target == [15, 47]:
                enemy_base = 2
                minimap_quadrant = 3 if self.location.base_top_left else 2
            elif minimap_target == [47, 15]:
                enemy_base = 3
                minimap_quadrant = 2 if self.location.base_top_left else 3
            elif minimap_target == [15, 15]:
                enemy_base = 4
                minimap_quadrant = 1 if self.location.base_top_left else 4
            #print("attack enemy's B"+str(enemy_base) + " (quadrant"+str(minimap_quadrant)+")")

            minimap_analyse = MinimapAnalyser().analyse(observations, self.location)
            enemy_buildings_positions = minimap_analyse.enemy_buildings_positions().positions(MinimapQuadrant(minimap_quadrant))

            if len(enemy_buildings_positions) == 0:
                #print("No building here, attack the mid of the zone")
                target = self.location.transform_location(int(self.x), int(self.y))
            else:
                #print("Attack just near the first building")
                building_to_attack = enemy_buildings_positions[0]
                # never attack directly the building to avoid to be attacked by enemy's without defending
                just_next_to_the_building = [building_to_attack[0] - 1, building_to_attack[1]]
                #print("always on a building? " + str(just_next_to_the_building in enemy_buildings_positions))
                #print(enemy_buildings_positions)
                #print(just_next_to_the_building)
                target = just_next_to_the_building

            #print(target)
            #print(MinimapQuadrantEnemyDetector().hot_sections(observations, self.location, minimap_target))

            return self.actions.attack_minimap(target, ActionQueueParameter().not_queued())

        return self.actions.no_op()
