
from nidup.pysc2.agent.commander import Commander
from nidup.pysc2.agent.order import Order
from nidup.pysc2.learning.qlearning import QLearningTable, QLearningTableStorage
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.agent.information import Location, BuildingCounter, EnemyDetector
from nidup.pysc2.agent.scripted.camera import CenterCameraOnCommandCenter, MoveCameraOnMinimapTarget
from nidup.pysc2.agent.multi.order.common import NoOrder
from nidup.pysc2.agent.multi.order.worker import PrepareSCVControlGroupsOrder, FillRefineryOnceBuilt, SendIdleSCVToMineral
from nidup.pysc2.agent.multi.order.train import BuildSCV
from nidup.pysc2.agent.multi.order.build import BuildSupplyDepot
from nidup.pysc2.agent.multi.learning.army import SmartActions, StateBuilder
from nidup.pysc2.agent.multi.learning.build import BuildOrderFactory

_PLAYER_ENEMY = 4


class MultiGameCommander(Commander):

    def __init__(self, base_location: Location, agent_name: str, enemy_detector: EnemyDetector):
        Commander.__init__(self)
        self.worker_commander = WorkerCommander(base_location)
        self.enemy_detector = enemy_detector
        self.scout_commander = ScoutCommander(base_location, self.enemy_detector)
        self.build_order_commander = BuildOrderCommander(base_location, agent_name)
        self.attack_commander = QLearningAttackCommander(base_location, agent_name, self.enemy_detector)
        self.current_order = None
        self.enemy_detector = enemy_detector

    def order(self, observations: Observations, step_index: int)-> Order:

        if not self.current_order:
            self.current_order = self.worker_commander.order(observations, step_index)

        elif self.current_order.done(observations):

            self.current_order = self.scout_commander.order(observations, step_index)
            if not isinstance(self.current_order, NoOrder):
                return self.current_order

            self.current_order = self.worker_commander.order(observations, step_index)
            if not isinstance(self.current_order, NoOrder):
                return self.current_order

            self.current_order = self.build_order_commander.order(observations, step_index)
            if not isinstance(self.current_order, NoOrder):
                return self.current_order

            # wait for the former build order to be finished
            if self.build_order_commander.build_is_finished(observations):
                self.current_order = self.attack_commander.order(observations, step_index)
            else:
                return self.current_order

        return self.current_order


class WorkerCommander(Commander):

    def __init__(self, base_location: Location):
        Commander.__init__(self)
        self.base_location = base_location
        self.control_group_order = PrepareSCVControlGroupsOrder(base_location)
        self.fill_refinery_one_order = FillRefineryOnceBuilt(base_location, 1)
        self.fill_refinery_two_order = FillRefineryOnceBuilt(base_location, 2)
        self.idle_scv_to_mineral = SendIdleSCVToMineral(base_location)
        self.current_order = self.control_group_order
        self.extra_scv_to_build_orders = []
        self._plan_to_build_scv_mineral_harvesters(4)
        self.last_played_step = 0
        self.number_steps_between_order = 30

    def order(self, observations: Observations, step_index: int)-> Order:
        if not self.current_order and self._can_play(step_index):
            if self.idle_scv_to_mineral.doable(observations):
                if self.idle_scv_to_mineral.done(observations):
                    self.idle_scv_to_mineral = SendIdleSCVToMineral(self.base_location)
                self.current_order = self.idle_scv_to_mineral
            elif self.fill_refinery_one_order.doable(observations) and not self.fill_refinery_one_order.done(observations):
                self.current_order = self.fill_refinery_one_order
                self._plan_to_build_scv_mineral_harvesters(3)
            elif self.fill_refinery_two_order.doable(observations) and not self.fill_refinery_two_order.done(observations):
                self.current_order = self.fill_refinery_two_order
                self._plan_to_build_scv_mineral_harvesters(3)
            elif self._has_scv_to_build(observations):
                self.current_order = self._scv_to_build_order(observations)

        elif self.current_order and self.current_order.done(observations):
            self._update_last_played_step(step_index)
            self.current_order = None
            return CenterCameraOnCommandCenter(self.base_location)

        if self.current_order:
            return self.current_order

        return NoOrder()

    def _plan_to_build_scv_mineral_harvesters(self, number: int):
        for index in range(number):
            self.extra_scv_to_build_orders.append(BuildSCV(self.base_location))

    def _has_scv_to_build(self, observations: Observations) -> bool:
        for order in self.extra_scv_to_build_orders:
            if order.doable(observations) and not order.done(observations):
                return True
        return False

    def _scv_to_build_order(self, observations: Observations) -> BuildSCV:
        for order in self.extra_scv_to_build_orders:
            if order.doable(observations) and not order.done(observations):
                return order
        return None

    def _update_last_played_step(self, step: int):
        self.last_played_step = step
        #print("worker played "+str(step))
        #print(self.current_order)

    def _can_play(self, step: int) -> bool:
        return self.last_played_step + self.number_steps_between_order < step


class ScoutCommander(Commander):

    def __init__(self, location: Location, enemy_detector: EnemyDetector):
        Commander.__init__(self)
        self.location = location
        self.enemy_detector = enemy_detector
        self.camera_order = None

    def order(self, observations: Observations, step_index: int)-> Order:
        if self.enemy_detector.race_detected():
            return NoOrder()

        elif self.camera_order:
            self.enemy_detector.detect_race(observations)
            self.camera_order = None
            #print(self.enemy_detector.race())
            return CenterCameraOnCommandCenter(self.location)

        elif self._see_enemy_on_minimap(observations):
            enemy_y, enemy_x = self._enemy_position_on_minimap(observations)
            self.camera_order = MoveCameraOnMinimapTarget(self.location, enemy_x[0], enemy_y[0])
            return self.camera_order

        return NoOrder()

    def _see_enemy_on_screen(self, observations: Observations) -> bool:
        enemy_y, enemy_x = (observations.screen().player_relative() == _PLAYER_ENEMY).nonzero()
        return enemy_y.any()

    def _see_enemy_on_minimap(self, observations: Observations) -> bool:
        enemy_y, enemy_x = self._enemy_position_on_minimap(observations)
        return enemy_y.any()

    def _enemy_position_on_minimap(self, observations: Observations) -> []:
        return (observations.minimap().player_relative() == _PLAYER_ENEMY).nonzero()


class BuildOrderCommander(Commander):

    def __init__(self, location: Location, agent_name: str):
        Commander.__init__(self)
        self.location = location
        self.agent_name = agent_name
        self.build_orders = BuildOrderFactory().create3RaxRushTvXWithFirstUnitsPush(location)
        self.current_order = None

    def order(self, observations: Observations, step_index: int)-> Order:
        if self.build_orders.finished(observations):
            return self._extra_supply_depots(observations)
        elif self.current_order and self.current_order.done(observations):
            self.current_order = None
            return CenterCameraOnCommandCenter(self.location)
        elif self.current_order and not self.current_order.done(observations):
            return self.current_order
        elif not self.current_order:
            order = self.build_orders.current(observations)
            if order.doable(observations):
                self.current_order = order
                return self.current_order
        return NoOrder()

    def build_is_finished(self, observations: Observations) -> bool:
        return self.build_orders.finished(observations)

    def _extra_supply_depots(self, observations: Observations) -> Order:
        counter = BuildingCounter()
        expectMore = 8 > counter.supply_depots_count(observations)
        supplyAlmostFull = observations.player().food_cap() - observations.player().food_used() <= 2
        if expectMore and supplyAlmostFull:
            return BuildSupplyDepot(self.location)
        else:
            return NoOrder()


class QLearningAttackCommander(Commander):

    def __init__(self, location: Location, agent_name: str, enemy_detector: EnemyDetector):
        super(Commander, self).__init__()
        self.location = location
        self.agent_name = agent_name
        self.enemy_detector = enemy_detector
        self.smart_actions = None
        self.qlearn = None
        self.previous_action = None
        self.previous_state = None
        self.previous_order = None

        self.smart_actions = SmartActions(self.location)
        self.qlearn = QLearningTable(actions=list(range(len(self.smart_actions.all()))))
        QLearningTableStorage().load(self.qlearn, self.agent_name)

    def order(self, observations: Observations, step_index: int)-> Order:
        if observations.last():
            self.qlearn.learn(str(self.previous_state), self.previous_action, observations.reward(), 'terminal')
            QLearningTableStorage().save(self.qlearn, self.agent_name)
            self.previous_action = None
            self.previous_state = None
            self.previous_order = None
            return NoOrder()

        if not self.previous_order or self.previous_order.done(observations):
            current_state = StateBuilder().build_state(self.location, observations, self.enemy_detector)
            if self.previous_action is not None:
                self.qlearn.learn(str(self.previous_state), self.previous_action, 0, str(current_state))
            rl_action = self.qlearn.choose_action(str(current_state))
            self.previous_state = current_state
            self.previous_action = rl_action
            self.previous_order = self.smart_actions.order(rl_action)

        return self.previous_order
