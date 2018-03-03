
import datetime
import pandas as pd
import numpy as np
import os


class GameResultsTable:
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.table = pd.DataFrame(columns=["Reward"], dtype=np.int8)
        self._load_file()
        print(self.table)

    def append(self, reward: int):
        now = datetime.datetime.now()
        self.table = self.table.append(pd.Series([reward], index=self.table.columns, name=now.isoformat()))
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
