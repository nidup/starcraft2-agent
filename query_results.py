
import sys
from getopt import getopt
from nidup.pysc2.dataviz.query import GameResultQueryBuilder


def query_game_results(agent_name: str, filter_name: str):

    builder = GameResultQueryBuilder()
    builder.query(agent_name, filter_name)


if __name__ == '__main__':
    try:
        opts, args = getopt(sys.argv[1:], "an:f", ["agent-name=", "filter="])
        for opt, arg in opts:
            if opt in ("-an", "--agent-name"):
                agent_name = arg
            elif opt in ("-f", "--filter"):
                filter_name = arg
        query_game_results(agent_name, filter_name)
    except getopt.GetoptError:
        sys.exit(2)
