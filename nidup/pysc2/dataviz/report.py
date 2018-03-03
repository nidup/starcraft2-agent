
from nidup.pysc2.learning.game_results import GameResultsTable
import matplotlib as mpl
mpl.use('Agg') # https://stackoverflow.com/questions/4931376/generating-matplotlib-graphs-without-a-running-x-server
import matplotlib.pyplot as plt
import os


class GameResultChart:

    def draw(self, agent_name: str) -> str:
        games = GameResultsTable(agent_name)

        # http://pandas.pydata.org/pandas-docs/stable/dsintro.html
        cumulated_percentage_win = []
        cumulated_percentage_draw = []
        cumulated_percentage_loss = []
        count_cumulated_win_games = 0
        count_cumulated_draw_games = 0
        count_cumulated_loss_games = 0
        total_parsed_games = 0
        for index in range(len(games.table)):
            total_parsed_games = total_parsed_games + 1
            count_cumulated_win_games = count_cumulated_win_games + games.table.iloc[index]['win']
            count_cumulated_draw_games = count_cumulated_draw_games + games.table.iloc[index]['draw']
            count_cumulated_loss_games = count_cumulated_loss_games + games.table.iloc[index]['loss']
            cumulated_percentage_win.append(count_cumulated_win_games / total_parsed_games * 100)
            cumulated_percentage_draw.append(count_cumulated_draw_games / total_parsed_games * 100)
            cumulated_percentage_loss.append(count_cumulated_loss_games / total_parsed_games * 100)

        line_win, = plt.plot(cumulated_percentage_win, label="Win %")
        line_draw, = plt.plot(cumulated_percentage_draw, label="Draw %")
        line_loss, = plt.plot(cumulated_percentage_loss, label="Loss %")

        plt.title('Game results')
        plt.xlabel('number of games')
        plt.ylabel('percentage of games')
        plt.legend(handles=[line_win, line_draw, line_loss])
        filepath = self._file_path(agent_name)
        plt.savefig(filepath)

        return filepath

    def _file_path(self, agent_name: str) -> str:
        root_folder = 'data'
        filename = agent_name + '_results.png'
        path = os.path.join(root_folder, filename)
        return path


class ScoreDetailsChart:

    def draw(self, agent_name: str) -> str:
        games = GameResultsTable(agent_name)

        # http://pandas.pydata.org/pandas-docs/stable/dsintro.html
        score_line = []
        for index in range(len(games.table)):
            score_line.append(games.table.iloc[index]['score'])

        line_score, = plt.plot(score_line, label="Score")
        plt.title('Score details')
        plt.xlabel('number of games')
        plt.ylabel('score')
        plt.legend(handles=[line_score])
        filepath = self._file_path(agent_name)
        plt.savefig(filepath)

        return filepath

    def _file_path(self, agent_name: str) -> str:
        root_folder = 'data'
        filename = agent_name + '_score_details.png'
        path = os.path.join(root_folder, filename)
        return path
