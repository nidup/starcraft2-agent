
import datetime
import pandas as pd
import numpy as np
import os
from nidup.pysc2.wrapper.observations import ScoreDetails


class GameResultsTable:
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.table = pd.DataFrame(
            columns=[
                "reward", "win", "draw", "loss",
                "score", "idle_production_time", "idle_worker_time", "total_value_units", "total_value_structures",
                "killed_value_units", "killed_value_structures", "collected_minerals", "collected_vespene",
                "collection_rate_minerals", "collection_rate_vespene", "spent_minerals", "spent_vespene"
            ],
            dtype=np.int8
        )
        self._load_file()

    def append(self, reward: int, score: ScoreDetails):
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
