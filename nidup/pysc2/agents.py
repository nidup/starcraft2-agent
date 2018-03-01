from pysc2.agents.base_agent import BaseAgent
from nidup.pysc2.commanders import GameCommander, ScoutingCommander
from nidup.pysc2.observations import Observations
from nidup.pysc2.information import BaseLocation
import time


class BuildOrderAgent(BaseAgent):

    commander = None
    debug = False

    def step(self, obs):
        super(BuildOrderAgent, self).step(obs)
        observations = Observations(obs)
        if self.commander is None:
            base_location = BaseLocation(observations)
            self.commander = GameCommander(base_location)
        if self.debug:
            time.sleep(0.5)
        return self.commander.order(observations).execute(observations)


class ScoutingAgent(BaseAgent):

    commander = None
    infinite_scouting = True

    def step(self, obs):
        super(ScoutingAgent, self).step(obs)
        observations = Observations(obs)
        if self.commander is None:
            base_location = BaseLocation(observations)
            self.commander = ScoutingCommander(base_location, self.infinite_scouting)
        return self.commander.order(observations).execute(observations)
