
import numpy as np
from nidup.pysc2.agent.commander import Commander
from nidup.pysc2.learning.qlearning import QLearningTable, QLearningTableStorage
from nidup.pysc2.agent.order import Order
from nidup.pysc2.agent.information import BuildingCounter, EnemyDetector, RaceNames
from nidup.pysc2.agent.scripted.camera import CenterCameraOnCommandCenter
from nidup.pysc2.agent.multi.order.common import NoOrder
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.agent.information import Location
from nidup.pysc2.agent.multi.order.common import SmartOrder
from nidup.pysc2.agent.multi.order.build import BuildSupplyDepot, BuildBarrack, BuildRefinery, BuildTechLabBarrack, BuildReactorBarrack
from nidup.pysc2.agent.multi.order.train import BuildMarine, BuildMarauder
from nidup.pysc2.agent.multi.order.research import ResearchCombatShield, ResearchConcussiveShells


class OrderedBuildOrder:

    def __init__(self, location: Location, name: str, ordered_orders: []):
        self.location = location
        self.name_data = name
        self.current_order = None
        self.current_order_index = 0
        self.ordered_orders = ordered_orders

    def current(self, observations: Observations) -> SmartOrder:
        if not self.current_order:
            self._next_order()
        elif self.current_order.done(observations):
            self._next_order()
        # TODO if not doable??
        # print(self.current_order)
        return self.current_order

    def finished(self, observations: Observations) -> bool:
        current_order_done = self.current_order and self.current_order.done(observations)
        is_last_order = self.current_order_index == len(self.ordered_orders)
        return current_order_done and is_last_order

    def name(self) -> str:
        return self.name_data

    def _next_order(self):
        self.current_order = self.ordered_orders[self.current_order_index]
        self.current_order_index = self.current_order_index + 1


class BuildOrdersCodes:

    def t3RaxRushTvX(self) -> str:
        return "3 Rax rush - TvX All-In"

    def t3RaxRushTvXFormerPush(self) -> str:
        return "3 Rax rush - TvX All-In - With Former Push"


class BuildOrderFactory:

    def create(self, code: str, location: Location) -> OrderedBuildOrder:
        # https://lotv.spawningtool.com/build/65735/
        if code == BuildOrdersCodes().t3RaxRushTvX():
            return OrderedBuildOrder(
                location,
                BuildOrdersCodes().t3RaxRushTvX(),
                [
                    BuildSupplyDepot(location),
                    BuildRefinery(location, 1),
                    BuildBarrack(location, 1),
                    BuildSupplyDepot(location),
                    BuildBarrack(location, 2),
                    BuildTechLabBarrack(location, 1),
                    BuildBarrack(location, 3),
                    ResearchCombatShield(location),
                    BuildReactorBarrack(location, 2),
                    BuildReactorBarrack(location, 3),
                    BuildSupplyDepot(location),
                    ResearchConcussiveShells(location),
                ]
            )
        # https://lotv.spawningtool.com/build/65735/
        elif code == BuildOrdersCodes().t3RaxRushTvXFormerPush():
            return OrderedBuildOrder(
                location,
                BuildOrdersCodes().t3RaxRushTvXFormerPush(),
                [
                    BuildSupplyDepot(location),
                    BuildRefinery(location, 1),
                    BuildBarrack(location, 1),
                    BuildSupplyDepot(location),
                    BuildBarrack(location, 2),
                    BuildTechLabBarrack(location, 1),
                    BuildBarrack(location, 3),
                    ResearchCombatShield(location),
                    BuildMarauder(location),
                    BuildReactorBarrack(location, 2),
                    BuildReactorBarrack(location, 3),
                    BuildSupplyDepot(location),
                    BuildMarauder(location),
                    BuildMarine(location),
                    BuildMarine(location),
                    BuildMarauder(location),
                    BuildMarine(location),
                    BuildMarine(location),
                    BuildMarine(location),
                    BuildMarine(location),
                    ResearchConcussiveShells(location),

                    # bigger timing push
                    # BuildMarine(location),
                    # BuildMarine(location),
                    # BuildMarine(location),
                    # BuildMarine(location),
                    # BuildMarauder(location),
                    # BuildMarauder(location),
                    #BuildBarrack(location, 4),
                    #BuildReactorBarrack(location, 4), NO REACTOR BUILT WHEN PLAY ON TOP GAME?
                ]
            )

        raise NotImplementedError("Can't create a build orders with code " + code)


class BuildOrderCommander(Commander):

    def __init__(self, location: Location, agent_name: str, enemy_detector: EnemyDetector):
        Commander.__init__(self)
        self.location = location
        self.agent_name = agent_name
        self.enemy_detector = enemy_detector
        self.build_orders = None
        self.current_order = None
        self.build_orders_selector = QLearningBuildOrdersSelector(self._commander_name(), self.enemy_detector)

    def order(self, observations: Observations)-> Order:
        # don't start before to know the enemy's race
        if not self.enemy_detector.race_detected():
            return NoOrder()
        elif not self.build_orders:
            print(self.enemy_detector.race())
            self.build_orders = self.build_orders_selector.select_build_order(self.location)
            #self.build_orders = BuildOrderFactory().create(BuildOrdersCodes().t3RaxRushTvX(), self.location)

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
        return self.build_orders and self.build_orders.finished(observations)

    def learn_on_last_episode_step(self, observations: Observations):
        self.build_orders_selector.learn_on_last_episode_step(observations)

    def current_build_orders(self) -> OrderedBuildOrder:
        return self.build_orders

    def _commander_name(self) -> str:
        return self.agent_name + "." + self.__class__.__name__

    def _extra_supply_depots(self, observations: Observations) -> Order:
        counter = BuildingCounter()
        expectMore = 8 > counter.supply_depots_count(observations)
        supplyAlmostFull = observations.player().food_cap() - observations.player().food_used() <= 2
        if expectMore and supplyAlmostFull:
            return BuildSupplyDepot(self.location)
        else:
            return NoOrder()


class StateBuilder:

    def build_state(self, enemy_detector: EnemyDetector) -> []:
        current_state = np.zeros(1)
        current_state[0] = self._enemy_race_id(enemy_detector)
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


class BuildOrdersActions:

    def __init__(self):
        self.build_orders_codes = [
            BuildOrdersCodes().t3RaxRushTvXFormerPush(),
            BuildOrdersCodes().t3RaxRushTvX()
        ]

    def all(self) -> []:
        return self.build_orders_codes

    def build_orders(self, code_idx: str, location: Location) -> OrderedBuildOrder:
        code = self.build_orders_codes[code_idx]
        print("Build orders " + code)
        return BuildOrderFactory().create(code, location)


class QLearningBuildOrdersSelector:

    def __init__(self, commander_name: str, enemy_detector: EnemyDetector):
        self.commander_name = commander_name
        self.enemy_detector = enemy_detector
        self.build_orders_actions = BuildOrdersActions()
        self.qlearn = QLearningTable(actions=list(range(len(self.build_orders_actions.all()))))
        QLearningTableStorage().load(self.qlearn, commander_name)
        self.previous_state = None
        self.previous_action = None

    def select_build_order(self, location: Location) -> OrderedBuildOrder:
        self.previous_state = StateBuilder().build_state(self.enemy_detector)
        self.previous_action = self.qlearn.choose_action(str(self.previous_state))
        build_orders = self.build_orders_actions.build_orders(self.previous_action, location)
        return build_orders

    def learn_on_last_episode_step(self, observations: Observations):
        self.qlearn.learn(str(self.previous_state), self.previous_action, observations.reward(), 'terminal')
        QLearningTableStorage().save(self.qlearn, self.commander_name)
