
from nidup.pysc2.agent.multi.info.player import Location
from nidup.pysc2.agent.multi.goal.common import OrderedGoal
from nidup.pysc2.agent.multi.order.build import BuildSupplyDepot, BuildBarrack, BuildRefinery, BuildTechLabBarrack, BuildReactorBarrack, BuildFactory, BuildStarport
from nidup.pysc2.agent.multi.order.research import ResearchCombatShield, ResearchConcussiveShells


class BuildOrdersGoal(OrderedGoal):

    def __init__(self, orders: []):
        OrderedGoal.__init__(self, orders)


class BuildOrdersGoalFactory:

    def build_3rax_1techlab_2reactors(self, location: Location) -> BuildOrdersGoal:
        return BuildOrdersGoal(
            [
                BuildSupplyDepot(location),
                BuildRefinery(location, 1),
                BuildBarrack(location, 1),
                BuildSupplyDepot(location),
                BuildBarrack(location, 2),
                BuildTechLabBarrack(location, 1),
                BuildBarrack(location, 3),
                ResearchCombatShield(location),
                BuildReactorBarrack(location, 2),
                BuildReactorBarrack(location, 3),
                BuildSupplyDepot(location),
                # BuildFactory(location, 1),
                # BuildStarport(location, 1),
                # BuildSupplyDepot(location),
                # BuildSupplyDepot(location),
                ResearchConcussiveShells(location),
            ]
        )
