
from pysc2.lib import actions
from nidup.pysc2.wrapper.observations import Observations


class Order:
    def done(self, observations: Observations) -> bool:
        raise NotImplementedError("Should be implemented by concrete order")

    def execute(self, observations: Observations) -> actions.FunctionCall:
        raise NotImplementedError("Should be implemented by concrete order")
