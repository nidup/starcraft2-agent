
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


class EnemyUnitsDetected:

    def __init__(self):
        self.detected_units = []

    def add(self, unit_id: int):
        self.detected_units.append(unit_id)
        self.detected_units = list(set(self.detected_units))
        #print(self.detected_units)

    def all(self) -> []:
        self.detected_units.sort()
        return self.detected_units


class EnemyUnitsExtractor:

    def extract(self, enemy_y: [], enemy_x: [], unit_types: []) -> EnemyUnitsDetected:
        #for i in range(0, 84):
        #    print(unit_types[i])

        unit_ids = []
        for unit_idx in range(0, len(enemy_y)):
            enemy_unit_id = unit_types[enemy_y[unit_idx]][enemy_x[unit_idx]]
            unit_ids.append(enemy_unit_id)

        unit_ids = list(set(unit_ids))

        return unit_ids


class EnemyUnitsDetector:

    def __init__(self):
        self.detected = EnemyUnitsDetected()
        self.units_extractor = EnemyUnitsExtractor()

    def detect_units(self, observations: Observations):
        enemy_y, enemy_x = (observations.screen().player_relative() == _PLAYER_ENEMY).nonzero()
        if enemy_y.any():
            # print("before")
            # print(enemy_y)
            # print(enemy_x)
            # print(observations.screen().unit_type())
            unit_types = observations.screen().unit_type()
            extracted_unit_ids = self.units_extractor.extract(enemy_y, enemy_x, unit_types)
            for enemy_unit_id in extracted_unit_ids:
                self.detected.add(enemy_unit_id)

    def detected_units(self) -> EnemyUnitsDetected:
        return self.detected
