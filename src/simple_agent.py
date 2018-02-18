from pysc2.agents import base_agent
from pysc2.lib import features

from terran_build_order import MMMTimingPushBuildOrder

import time

# Features
_PLAYER_RELATIVE = features.SCREEN_FEATURES.player_relative.index

# Parameters
_PLAYER_SELF = 1

class SimpleAgent(base_agent.BaseAgent):

    build_order = None

    def step(self, obs):
        super(SimpleAgent, self).step(obs)

        if self.build_order is None:
            player_y, player_x = (obs.observation["minimap"][_PLAYER_RELATIVE] == _PLAYER_SELF).nonzero()
            base_top_left = player_y.mean() <= 31
            self.build_order = MMMTimingPushBuildOrder(base_top_left)

        #time.sleep(0.5)

        return self.build_order.action(obs)
