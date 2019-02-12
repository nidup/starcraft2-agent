
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.agent.order import Order


class Commander:

    def order(self, observations: Observations)-> Order:
        raise NotImplementedError("Should be implemented by concrete commander")
