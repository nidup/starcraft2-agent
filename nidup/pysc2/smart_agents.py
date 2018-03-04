
from nidup.pysc2.agent.smart.commander import QLearningCommander
from nidup.pysc2.wrapper.observations import Observations
from pysc2.agents.base_agent import BaseAgent


class ReinforcementAgent(BaseAgent):

    def __init__(self):
        super(ReinforcementAgent, self).__init__()
        self.commander = None

    def step(self, obs):
        super(ReinforcementAgent, self).step(obs)
        observations = Observations(obs)
        if observations.first():
            self.commander = QLearningCommander(self.name())

        return self.commander.order(observations).execute(observations)

    def name(self) -> str:
        return __name__ + "." + self.__class__.__name__
