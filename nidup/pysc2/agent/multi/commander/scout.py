
from nidup.pysc2.agent.commander import Commander
from nidup.pysc2.agent.order import Order
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.agent.information import Location, EnemyDetector
from nidup.pysc2.agent.scripted.camera import CenterCameraOnCommandCenter, MoveCameraOnMinimapTarget
from nidup.pysc2.agent.multi.order.common import NoOrder
from nidup.pysc2.agent.multi.order.scout import ScoutWithScv

_PLAYER_ENEMY = 4


class ScoutCommander(Commander):

    def __init__(self, location: Location, enemy_detector: EnemyDetector):
        Commander.__init__(self)
        self.location = location
        self.enemy_detector = enemy_detector
        self.scout_order = ScoutWithScv(location)
        self.camera_order = None

    def order(self, observations: Observations, step_index: int)-> Order:
        if self.enemy_detector.race_detected():
            return NoOrder()

        if not self.scout_order.done(observations):
            return self.scout_order

        elif self.camera_order:
            self.enemy_detector.detect_race(observations)
            self.camera_order = None
            return CenterCameraOnCommandCenter(self.location)

        elif self._see_enemy_on_minimap(observations):
            enemy_y, enemy_x = self._enemy_position_on_minimap(observations)
            self.camera_order = MoveCameraOnMinimapTarget(self.location, enemy_x[0], enemy_y[0])
            return self.camera_order

        return NoOrder()

    def _see_enemy_on_screen(self, observations: Observations) -> bool:
        enemy_y, enemy_x = (observations.screen().player_relative() == _PLAYER_ENEMY).nonzero()
        return enemy_y.any()

    def _see_enemy_on_minimap(self, observations: Observations) -> bool:
        enemy_y, enemy_x = self._enemy_position_on_minimap(observations)
        return enemy_y.any()

    def _enemy_position_on_minimap(self, observations: Observations) -> []:
        return (observations.minimap().player_relative() == _PLAYER_ENEMY).nonzero()
