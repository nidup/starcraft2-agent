from pysc2.agents import base_agent

from terran_build_order import MMMTimingPushBuildOrder
from observations import Observations

import time

# Parameters
_PLAYER_SELF = 1


class SimpleAgent(base_agent.BaseAgent):

    build_order = None
    debug = False

    def step(self, obs):
        super(SimpleAgent, self).step(obs)
        observations = Observations(obs)
        if self.build_order is None:
            player_y, player_x = (observations.minimap().player_relative() == _PLAYER_SELF).nonzero()
            base_top_left = player_y.mean() <= 31
            self.build_order = MMMTimingPushBuildOrder(base_top_left)
        if self.debug:
            time.sleep(0.5)
        return self.build_order.action(observations)
