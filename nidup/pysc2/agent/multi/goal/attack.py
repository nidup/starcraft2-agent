
import random
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.agent.multi.order.common import SmartOrder, NoOrder
from nidup.pysc2.agent.multi.order.attack import SeekAndDestroyBuildingAttack,SeekAndDestroyAllUnitsAttack
from nidup.pysc2.agent.multi.commander.attack import AttackCommander
from nidup.pysc2.agent.multi.goal.common import Goal
from nidup.pysc2.agent.multi.minimap.analyser import MinimapAnalyser, MinimapQuadrant
from nidup.pysc2.agent.information import Location


class AttackQuadrantGoal(Goal):

    def __init__(self, attack_commander: AttackCommander):
        self.attack_commander = attack_commander
        self.current_order = None

    def order(self, observations: Observations) -> SmartOrder:
        if not self.current_order:
            self.current_order = self.attack_commander.order(observations)
        if not self.current_order.done(observations):
            return self.current_order

    def done(self, observations: Observations) -> bool:
        return self.current_order and self.current_order.done(observations)


class SeekAndDestroyQuadrantGoal(Goal):

    def __init__(self, location: Location):
        self.location = location
        self.current_order = None
        self.noop_orders = []
        for idx in range(0, 20):
            self.noop_orders.append(NoOrder())

    def order(self, observations: Observations) -> SmartOrder:
        if not self.current_order:
            self.current_order = self._seek_and_destroy_orders(observations, self.location)
        if not self.current_order.done(observations):
            return self.current_order
        noop_order = self.noop_orders.pop(0)
        return noop_order

    def done(self, observations: Observations) -> bool:
        return len(self.noop_orders) == 0

    def _seek_and_destroy_orders(self, observations: Observations, location: Location) -> SmartOrder:
        print("seek and destroy order - late game")
        map_analyse = MinimapAnalyser().analyse(observations, location)
        quadrants = [MinimapQuadrant(1), MinimapQuadrant(2), MinimapQuadrant(3), MinimapQuadrant(4)]

        # start by the most probable enemy's base depending on player's base location
        if self.location.command_center_is_top_left():
            quadrants = quadrants[::-1]

        # seek and destroy buildings if there are
        for quadrant in quadrants:
            buildings = map_analyse.enemy_buildings_positions().positions(quadrant)
            if len(buildings) > 0:
                return SeekAndDestroyBuildingAttack(self.location, quadrant)

        # seek and destroy single units if there are
        for quadrant in quadrants:
            units = map_analyse.all_enemy_positions().positions(quadrant)
            if len(units) > 0:
                return SeekAndDestroyAllUnitsAttack(self.location, quadrant)

        # attack randomly, one after the other
        index = random.randint(0, len(quadrants) - 1)
        print("nothing on minimap, attack randomly the quadrant number "+str(index+1))
        return SeekAndDestroyBuildingAttack(self.location, quadrants[index])
