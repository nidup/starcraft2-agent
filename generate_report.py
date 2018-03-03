
import sys
from getopt import getopt
from nidup.pysc2.dataviz.report import GameResultChart, ScoreDetailsChart


def generate_game_results_report(agent_name: str):

    file_path = GameResultChart().draw(agent_name)
    print("GameResultChart has been generated in "+file_path)

    file_path = ScoreDetailsChart().draw(agent_name)
    print("ScoreDetailsChart has been generated in "+file_path)


if __name__ == '__main__':
    try:
        opts, args = getopt(sys.argv[1:], "an", ["agent-name="])
        for opt, arg in opts:
            if opt in ("-an", "--agent-name"):
                agent_name = arg
            generate_game_results_report(agent_name)
    except getopt.GetoptError:
        sys.exit(2)
