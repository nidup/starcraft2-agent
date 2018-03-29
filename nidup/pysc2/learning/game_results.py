
import datetime
import pandas as pd
import numpy as np
import os
from nidup.pysc2.wrapper.observations import ScoreDetails


class FinishedGameInformationDetails:

    def __init__(self, last_episode_step: int, enemy_race: str, build_order: str, enemy_units: str):
        self.last_episode_step_data = last_episode_step
        self.enemy_race_data = enemy_race
        self.build_order_data = build_order
        self.detected_enemy_units_data = enemy_units

    def last_episode_step(self) -> int:
        return self.last_episode_step_data

    def enemy_race(self) -> str:
        return self.enemy_race_data

    def build_order(self) -> str:
        return self.build_order_data

    def detected_enemy_units(self) -> str:
        return self.detected_enemy_units_data


class GameResultsTable:
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.table = pd.DataFrame(
            columns=[
                "reward", "win", "draw", "loss",
                "score", "idle_production_time", "idle_worker_time", "total_value_units", "total_value_structures",
                "killed_value_units", "killed_value_structures", "collected_minerals", "collected_vespene",
                "collection_rate_minerals", "collection_rate_vespene", "spent_minerals", "spent_vespene",
                "last_episode_step", "enemy_race", "build_order", "enemy_units"
            ],
            dtype=np.int8
        )
        self._load_file()

    def append(self, reward: int, score: ScoreDetails, details: FinishedGameInformationDetails):
        now = datetime.datetime.now()
        if reward > 0:
            row = [reward, 1, 0, 0]
        elif reward < 0:
            row = [reward, 0, 0, 1]
        else:
            row = [reward, 0, 1, 0]
        row = row + [
            score.score(),
            score.idle_production_time(),
            score.idle_worker_time(),
            score.total_value_units(),
            score.total_value_structures(),
            score.killed_value_units(),
            score.killed_value_structures(),
            score.collected_minerals(),
            score.collected_vespene(),
            score.collection_rate_minerals(),
            score.collection_rate_vespene(),
            score.spent_minerals(),
            score.spent_vespene(),
            details.last_episode_step(),
            details.enemy_race(),
            details.build_order(),
            details.detected_enemy_units()
        ]
        self.table = self.table.append(pd.Series(row, index=self.table.columns, name=now.isoformat()))
        self._write_file()

    def _load_file(self):
        if os.path.isfile(self._file_path()):
            self.table = pd.read_pickle(self._file_path(), compression='gzip')

    def _write_file(self):
        self.table.to_pickle(self._file_path(), 'gzip')

    def _file_path(self) -> str:
        root_folder = 'data'
        filename = self.agent_name + '_results.gz'
        path = os.path.join(root_folder, filename)
        return path
