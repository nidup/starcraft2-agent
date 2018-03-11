
from nidup.pysc2.agent.commander import Commander
from nidup.pysc2.agent.order import Order
from nidup.pysc2.learning.qlearning import QLearningTable, QLearningTableStorage
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.agent.information import Location, BuildingCounter
from nidup.pysc2.agent.scripted.camera import CenterCameraOnCommandCenter
from nidup.pysc2.agent.smart.orders import NoOrder, PrepareSCVControlGroupsOrder, FillRefineryOnceBuilt, BuildSCV, SendIdleSCVToMineral
from nidup.pysc2.agent.hybrid.attack import SmartActions, StateBuilder
from nidup.pysc2.agent.hybrid.build import BuildOrder


class HybridGameCommander(Commander):

    def __init__(self, base_location: Location, agent_name: str):
        Commander.__init__(self)
        self.worker_commander = WorkerCommander(base_location)
        self.build_order_commander = BuildOrderCommander(base_location, agent_name)
        self.attack_commander = QLearningAttackCommander(base_location, agent_name)

    def order(self, observations: Observations)-> Order:
        order = self.worker_commander.order(observations)
        if not isinstance(order, NoOrder):
            return order

        order = self.build_order_commander.order(observations)
        if not isinstance(order, NoOrder):
            return order

        return self.attack_commander.order(observations)


class WorkerCommander(Commander):

    def __init__(self, base_location: Location):
        Commander.__init__(self)
        self.base_location = base_location
        self.control_group_order = PrepareSCVControlGroupsOrder(base_location)
        self.fill_refinery_one_order = FillRefineryOnceBuilt(base_location, 1)
        self.fill_refinery_two_order = FillRefineryOnceBuilt(base_location, 2)
        self.train_scv_order = BuildSCV(base_location)
        self.train_scv_order_two = BuildSCV(base_location)
        self.train_scv_order_three = BuildSCV(base_location)
        self.idle_scv_to_mineral = SendIdleSCVToMineral(base_location)
        self.current_order = self.control_group_order

    def order(self, observations: Observations)-> Order:
        if not self.current_order:
            if self.idle_scv_to_mineral.doable(observations):
                if self.idle_scv_to_mineral.done(observations):
                    self.idle_scv_to_mineral = SendIdleSCVToMineral(self.base_location)
                self.current_order = self.idle_scv_to_mineral
            elif self.fill_refinery_one_order.doable(observations) and not self.fill_refinery_one_order.done(observations):
                self.current_order = self.fill_refinery_one_order
            elif self.fill_refinery_two_order.doable(observations) and not self.fill_refinery_two_order.done(observations):
                self.current_order = self.fill_refinery_two_order
            #elif self.fill_refinery_one_order.done(observations):
                #if self.train_scv_order.doable(observations) and not self.train_scv_order.done(observations):
                #    self.current_order = self.train_scv_order
                #elif self.train_scv_order_two.doable(observations) and not self.train_scv_order_two.done(observations):
                #    self.current_order = self.train_scv_order_two
                #elif self.train_scv_order_three.doable(observations) and not self.train_scv_order_three.done(observations):
                #    self.current_order = self.train_scv_order_three

        elif self.current_order and self.current_order.done(observations):
            self.current_order = None
            return CenterCameraOnCommandCenter(self.base_location)

        if self.current_order:
            print(self.current_order)
            return self.current_order

        return NoOrder()


class BuildOrderCommander(Commander):

    def __init__(self, location: Location, agent_name: str):
        Commander.__init__(self)
        self.location = location
        self.agent_name = agent_name
        self.build_orders = BuildOrder(self.location)
        self.current_order = None

    def order(self, observations: Observations)-> Order:
        if self.build_orders.finished(observations):
            return NoOrder()
        elif self.current_order and self.current_order.done(observations):
            self.current_order = None
            return CenterCameraOnCommandCenter(self.location)
        else:
            self.current_order = self.build_orders.current(observations)
            return self.current_order


class QLearningAttackCommander(Commander):

    def __init__(self, location: Location, agent_name: str):
        super(Commander, self).__init__()
        self.location = location
        self.agent_name = agent_name
        self.smart_actions = None
        self.qlearn = None
        self.previous_action = None
        self.previous_state = None
        self.previous_order = None
        self.location = location

        self.smart_actions = SmartActions(self.location)
        self.qlearn = QLearningTable(actions=list(range(len(self.smart_actions.all()))))
        QLearningTableStorage().load(self.qlearn, self.agent_name)

    def order(self, observations: Observations)-> Order:
        if observations.last():
            self.qlearn.learn(str(self.previous_state), self.previous_action, observations.reward(), 'terminal')
            QLearningTableStorage().save(self.qlearn, self.agent_name)
            self.previous_action = None
            self.previous_state = None
            self.previous_order = None
            return NoOrder()

        if not self.previous_order or self.previous_order.done(observations):
            current_state = StateBuilder().build_state(self.location, observations)
            if self.previous_action is not None:
                self.qlearn.learn(str(self.previous_state), self.previous_action, 0, str(current_state))
            rl_action = self.qlearn.choose_action(str(current_state))
            self.previous_state = current_state
            self.previous_action = rl_action
            self.previous_order = self.smart_actions.order(rl_action)

        return self.previous_order
