
from nidup.pysc2.agent.information import Location
from nidup.pysc2.agent.multi.goal.common import OrderedGoal
from nidup.pysc2.agent.multi.order.train import BuildMarine, BuildMarauder, BuildHellion, BuildMedivac


class TrainSquadGoal(OrderedGoal):

    def __init__(self, orders: []):
        OrderedGoal.__init__(self, orders)


class TrainSquadGoalFactory:

    def train_7marines_3marauders(self, location: Location) -> TrainSquadGoal:
        return TrainSquadGoal(
            [
                BuildMarine(location),
                BuildMarine(location),
                BuildMarine(location),
                BuildMarine(location),
                BuildMarine(location),
                BuildMarine(location),
                BuildMarine(location),
                BuildMarauder(location),
                BuildMarauder(location),
                BuildMarauder(location),
            ]
        )
