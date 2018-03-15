
from nidup.pysc2.learning.game_results import GameResultsTable


class GameResultQueryBuilder:

    def query(self, agent_name: str, filter: str):
        games = GameResultsTable(agent_name)
        available_filters = ['win', 'loss', 'draw']
        if not filter in available_filters:
            raise Exception('The filter "'+filter+'" is unknown, available filters are '+', '.join(available_filters))

        # http://pandas.pydata.org/pandas-docs/stable/dsintro.html
        total_games = 0
        total_filtered_games = 0
        for index in range(len(games.table)):
            total_games = total_games + 1
            if games.table.iloc[index][filter] == 1:
                total_filtered_games = total_filtered_games + 1
                print("\n"+str(games.table.iloc[index]))

        print("\nTotal filtered "+str(total_filtered_games) + " (on "+str(total_games)+")")
