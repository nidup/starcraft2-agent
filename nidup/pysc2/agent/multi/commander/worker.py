
from nidup.pysc2.agent.commander import Commander
from nidup.pysc2.agent.order import Order
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.agent.information import Location, EpisodeDetails
from nidup.pysc2.agent.scripted.camera import CenterCameraOnCommandCenter
from nidup.pysc2.agent.multi.order.common import NoOrder
from nidup.pysc2.agent.multi.order.worker import PrepareSCVControlGroupsOrder, FillRefineryOnceBuilt, SendIdleSCVToMineral
from nidup.pysc2.agent.multi.order.train import BuildSCV


class WorkerCommander(Commander):

    def __init__(self, base_location: Location, episode_details: EpisodeDetails):
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
        self.episode_details = episode_details

    def order(self, observations: Observations)-> Order:
        if not self.current_order and self._can_play():
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
            self._update_last_played_step()
            self.current_order = None
            return CenterCameraOnCommandCenter(self.base_location)

        if self.current_order:
            print("worker current order")
            print(self.current_order)
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

    def _update_last_played_step(self):
        self.last_played_step = self.episode_details.episode_step()

    def _can_play(self) -> bool:
        return self.last_played_step + self.number_steps_between_order < self.episode_details.episode_step()
