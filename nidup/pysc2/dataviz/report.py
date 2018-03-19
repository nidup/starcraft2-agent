
from nidup.pysc2.learning.game_results import GameResultsTable
import matplotlib as mpl
mpl.use('Agg') # https://stackoverflow.com/questions/4931376/generating-matplotlib-graphs-without-a-running-x-server
import matplotlib.pyplot as plt
import os
from nidup.pysc2.agent.multi.commander.build import BuildOrdersActions


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
        plt.gcf().clear()

        return filepath

    def _file_path(self, agent_name: str) -> str:
        root_folder = 'data'
        filename = agent_name + '_results.png'
        path = os.path.join(root_folder, filename)
        return path


class GameResultChartPerEnemyRace:

    def draw(self, agent_name: str, enemy_race: str) -> str:
        games = GameResultsTable(agent_name)

        cumulated_percentage_win = []
        cumulated_percentage_draw = []
        cumulated_percentage_loss = []
        count_cumulated_win_games = 0
        count_cumulated_draw_games = 0
        count_cumulated_loss_games = 0
        total_parsed_games = 0
        for index in range(len(games.table)):
            if games.table.iloc[index]['enemy_race'] == enemy_race:
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

        plt.title('Game results against '+enemy_race)
        plt.xlabel('number of games')
        plt.ylabel('percentage of games')
        plt.legend(handles=[line_win, line_draw, line_loss])
        filepath = self._file_path(agent_name, enemy_race)
        plt.savefig(filepath)
        plt.gcf().clear()

        return filepath

    def _file_path(self, agent_name: str, enemy_race: str) -> str:
        root_folder = 'data'
        filename = agent_name + '_results_' + enemy_race + '.png'
        path = os.path.join(root_folder, filename)
        return path


class BuildOrdersChartPerEnemyRace:

    def draw(self, agent_name: str, enemy_race: str) -> str:

        if not agent_name == "nidup.pysc2.agents.MultiReinforcementAgent":
            print("Agent "+agent_name+" is not supported by this report")

        games = GameResultsTable(agent_name)

        cumulated_percentage_per_build_order = {}
        count_cumulated_per_build_order = {}
        build_orders_codes = BuildOrdersActions().all()
        for build_order_code in build_orders_codes:
            cumulated_percentage_per_build_order[build_order_code] = []
            count_cumulated_per_build_order[build_order_code] = 0

        total_parsed_games = 0
        for index in range(len(games.table)):
            if games.table.iloc[index]['enemy_race'] == enemy_race:
                total_parsed_games = total_parsed_games + 1
                build_order = games.table.iloc[index]['build_order']
                count_cumulated_per_build_order[build_order] = count_cumulated_per_build_order[build_order] + 1
                for each_build_order_code in build_orders_codes:
                    cumulated_percentage_per_build_order[each_build_order_code].append(count_cumulated_per_build_order[each_build_order_code] / total_parsed_games * 100)

        lines = []
        for build_order_code in build_orders_codes:
            line, = plt.plot(cumulated_percentage_per_build_order[build_order_code], label=build_order_code)
            lines.append(line)

        plt.title('Build orders against '+enemy_race)
        plt.xlabel('number of games')
        plt.ylabel('percentage of games')
        plt.legend(handles=lines)
        filepath = self._file_path(agent_name, enemy_race)
        plt.savefig(filepath)
        plt.gcf().clear()

        return filepath

    def _file_path(self, agent_name: str, enemy_race: str) -> str:
        root_folder = 'data'
        filename = agent_name + '_build_orders_' + enemy_race + '.png'
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
        plt.gcf().clear()

        return filepath

    def _file_path(self, agent_name: str) -> str:
        root_folder = 'data'
        filename = agent_name + '_score_details.png'
        path = os.path.join(root_folder, filename)
        return path


class LastGamesStatsPerRaceTable:

    def print(self, agent_name: str, number_games: int = 100):
        print("\nResults on the "+str(number_games)+" last games:")
        print("race\ttotal\twin\tdraw\tloss\twin %\tdraw %\tloss %")
        for race in ['zerg', 'terran', 'protoss']:
            row = self._game_stats_per_race(agent_name, number_games, race)
            print(row['race']+"\t"+str(row['total'])+"\t"+str(row['win'])+"\t"+str(row['draw'])+"\t"+str(row['loss'])+"\t"+str(row['win %'])+"\t"+str(row['draw %'])+"\t"+str(row['loss %']))

    def _game_stats_per_race(self, agent_name: str, number_games: int, enemy_race: str) -> []:
        games = GameResultsTable(agent_name)
        count_cumulated_win_games = 0
        count_cumulated_draw_games = 0
        count_cumulated_loss_games = 0
        total_parsed_games = 0
        total_games = len(games.table)
        start_index = total_games - number_games
        for index in range(total_games):
            if index >= start_index and games.table.iloc[index]['enemy_race'] == enemy_race:
                total_parsed_games = total_parsed_games + 1
                count_cumulated_win_games = count_cumulated_win_games + games.table.iloc[index]['win']
                count_cumulated_draw_games = count_cumulated_draw_games + games.table.iloc[index]['draw']
                count_cumulated_loss_games = count_cumulated_loss_games + games.table.iloc[index]['loss']

        percentage_win = 0
        if count_cumulated_win_games > 0:
            percentage_win = count_cumulated_win_games / total_parsed_games * 100

        percentage_draw = 0
        if count_cumulated_draw_games > 0:
            percentage_draw = count_cumulated_draw_games / total_parsed_games * 100

        percentage_loss = 0
        if count_cumulated_loss_games > 0:
            percentage_loss = count_cumulated_loss_games / total_parsed_games * 100

        return {
            'total': total_parsed_games,
            'race': enemy_race,
            'win': count_cumulated_win_games,
            'draw': count_cumulated_draw_games,
            'loss': count_cumulated_loss_games,
            'win %': round(percentage_win, 2),
            'draw %': round(percentage_draw, 2),
            'loss %': round(percentage_loss, 2)
        }
