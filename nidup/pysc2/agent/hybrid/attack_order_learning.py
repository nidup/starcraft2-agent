
import random
from pysc2.lib import actions
from nidup.pysc2.agent.smart.orders import SmartOrder
from nidup.pysc2.agent.information import Location
from nidup.pysc2.wrapper.observations import Observations


class QLearningAttack(SmartOrder):

    def __init__(self, location: Location, x: int , y: int):
        SmartOrder.__init__(self, location)
        self.step = 0
        self.x = x
        self.y = y

    def doable(self, observations: Observations) -> bool:
        return True

    def done(self, observations: Observations) -> bool:
        return self.step == 2

    def execute(self, observations: Observations) -> actions.FunctionCall:
        self.step = self.step + 1
        if self.step == 1:
            return self.select_army(observations)
        elif self.step == 2:
            return self.attack_minimap(observations)

    def select_army(self, observations: Observations) -> actions.FunctionCall:
        if self.action_ids.select_army() in observations.available_actions():
            return self.actions.select_army()

        return self.actions.no_op()

    def attack_minimap(self, observations: Observations) -> actions.FunctionCall:
        do_it = True
        if not observations.single_select().empty() and observations.single_select().unit_type() == self.unit_type_ids.terran_scv():
            do_it = False
        if not observations.multi_select().empty() and observations.multi_select().unit_type(0) == self.unit_type_ids.terran_scv():
            do_it = False

        if do_it and self.action_ids.attack_minimap() in observations.available_actions():
            x_offset = random.randint(-1, 1)
            y_offset = random.randint(-1, 1)
            target = self.location.transform_location(int(self.x) + (x_offset * 8), int(self.y) + (y_offset * 8))

            return self.actions.attack_minimap(target)

        return self.actions.no_op()
