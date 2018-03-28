
from nidup.pysc2.wrapper.observations import Observations
from nidup.pysc2.wrapper.unit_types import AllUnitTypeIdsPerRace

_PLAYER_ENEMY = 4


class RaceNames:

    def unknown(self) -> str:
        return "unknown"

    def protoss(self) -> str:
        return "protoss"

    def terran(self) -> str:
        return "terran"

    def zerg(self) -> str:
        return "zerg"


class EnemyRaceDetector:

    def __init__(self):
        self.enemy_race = RaceNames().unknown()

    def race(self) -> str:
        return self.enemy_race

    def race_detected(self) -> bool:
        return self.enemy_race != RaceNames().unknown()

    def detect_race(self, observations: Observations):
        enemy_y, enemy_x = (observations.screen().player_relative() == _PLAYER_ENEMY).nonzero()
        if enemy_y.any():
            unit_type = observations.screen().unit_type()
            for unit_id in AllUnitTypeIdsPerRace().zerg():
                unit_y, unit_x = (unit_type == unit_id).nonzero()
                if unit_y.any():
                    self.enemy_race = RaceNames().zerg()

            unit_type = observations.screen().unit_type()
            for unit_id in AllUnitTypeIdsPerRace().protoss():
                unit_y, unit_x = (unit_type == unit_id).nonzero()
                if unit_y.any():
                    self.enemy_race = RaceNames().protoss()

            if not self.race_detected():
                self.enemy_race = RaceNames().terran()
