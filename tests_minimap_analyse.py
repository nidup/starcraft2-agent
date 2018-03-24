
from nidup.pysc2.agent.multi.minimap.analyser import MinimapEnemyAnalyse, MinimapQuadrant


class BuildingExpectations:
    def __init__(self, bases: int, buildings: int):
        self.bases = bases
        self.buildings = buildings


class BuildingPositionExpectations:
    def __init__(self, quadrant1: [], quadrant2: [], quadrant3: []):
        self.quadrant1 = quadrant1
        self.quadrant2 = quadrant2
        self.quadrant3 = quadrant3


class MinimapCase:

    def __init__(self, description: str, enemy_y: [], enemy_x: [], expectations: BuildingExpectations, positions: BuildingPositionExpectations):
        self.enemy_y = enemy_y
        self.enemy_x = enemy_x
        self.description = description
        self.expectations = expectations
        self.positions = positions


if __name__ == '__main__':

    cases = [
        MinimapCase(
            "playing top left, expecting an enemy's base in bottom right",
            [44, 44, 44, 45, 45, 45, 45, 45, 46, 46, 46, 46, 46, 47, 48, 49, 49, 49, 50, 50, 50],
            [38, 39, 40, 35, 36, 38, 39, 40, 35, 36, 38, 39, 40, 34, 32, 33, 37, 38, 34, 37, 38],
            BuildingExpectations(1, 3),
            BuildingPositionExpectations([], [], [])
        ),
        MinimapCase(
            "playing top left, expecting an enemy's base in bottom right and a spread enemy's unit in the bottom left",
            [44, 44, 44, 45, 45, 45, 46, 46, 46, 46, 49, 49, 50, 50],
            [38, 39, 40, 38, 39, 40, 18, 38, 39, 40, 37, 38, 37, 38],
            BuildingExpectations(1, 2),
            BuildingPositionExpectations([], [], [])
        ),
        MinimapCase(
            "playing top left, expecting 2 enemy's bases and being under attack",
            [19, 20, 21, 22, 22, 23, 24, 43, 43, 44, 44, 44, 44, 44, 44, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 46,
             46, 46, 46, 46, 46, 46, 46, 46, 46, 47, 47, 47, 47, 47, 47, 48, 48, 48, 48, 48, 49, 49, 49, 49, 49, 49,
             50, 50, 50, 50, 50, 50, 52, 52, 52, 52, 53, 53, 53],
            [22, 25, 18, 23, 25, 25, 25, 33, 34, 28, 33, 34, 38, 39, 40, 11, 12, 25, 29, 30, 35, 36, 38, 39, 40, 11, 12,
             29, 30, 34, 35, 36, 38, 39, 40, 16, 17, 18, 34, 35, 36, 16, 17, 18, 35, 36, 16, 17, 18, 34, 37, 38, 17, 18,
             34, 35, 37, 38, 15, 18, 19, 20, 16, 19, 20],
            BuildingExpectations(2, 10),
            BuildingPositionExpectations(
                [],
                [],
                [[11, 45], [12, 45], [29, 45], [30, 45], [11, 46], [12, 46], [29, 46], [30, 46], [16, 47], [17, 47],
                 [18, 47], [16, 48], [17, 48], [18, 48], [16, 49], [17, 49], [18, 49], [17, 50], [18, 50], [19, 52],
                 [20, 52], [19, 53], [20, 53]]
            )
        ),
        MinimapCase(
            "playing bottom right, expecting 2 enemy's base",
            [20, 20, 20, 21, 21, 21, 21, 21, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 23, 23, 23, 23, 23, 24, 24, 24,
             24, 25, 25, 26, 26, 39],
            [40, 41, 42, 22, 23, 40, 41, 42, 18, 19, 20, 22, 23, 25, 40, 41, 42, 45, 46, 18, 19, 20, 45, 46, 18, 19, 20,
             28, 22, 23, 22, 23, 44],
            BuildingExpectations(2, 5),
            BuildingPositionExpectations(
                [[22, 21], [23, 21], [18, 22], [19, 22], [20, 22], [22, 22], [23, 22], [18, 23], [19, 23], [20, 23],
                 [18, 24], [19, 24], [20, 24], [22, 25], [23, 25], [22, 26], [23, 26]],
                [[40, 20], [41, 20], [42, 20], [40, 21], [41, 21], [42, 21], [40, 22], [41, 22], [42, 22], [45, 22],
                 [46, 22], [45, 23], [46, 23]],
                []
            )
        )
    ]

    for case in cases:
        print("-" * 200)
        print(case.description)
        print("-" * 200)
        analyse = MinimapEnemyAnalyse(case.enemy_y, case.enemy_x)
        print("All visible enemies")
        print(analyse.all_enemies())
        print("All visible enemy's building")
        print(analyse.all_enemies_building())
        print("All visible enemy's main building")
        print(analyse.all_enemies_main_buildings())
        if case.expectations.bases == analyse.all_enemies_main_buildings().count():
            print("Number of main buildings is [OK]")
        else:
            raise RuntimeError(
                "Expect to detect "+str(case.expectations.bases)+" main buildings and not "+str(analyse.all_enemies_main_buildings().count())
            )
        if case.expectations.buildings == analyse.all_enemies_building().count():
            print("Number of buildings is [OK]")
        else:
            raise RuntimeError(
                "Expect to detect "+str(case.expectations.buildings)+" buildings and not "+str(analyse.all_enemies_building().count())
            )
        if case.positions.quadrant1 == analyse.enemy_buildings_positions().positions(MinimapQuadrant(1)):
            print("Position of buildings in quadrant1 is [OK]")
        else:
            raise RuntimeError(
                "Expect the following buildings position for Q1 " + str(case.positions.quadrant1) + " and not " + str(
                    analyse.enemy_buildings_positions().positions(MinimapQuadrant(1)))
            )
        if case.positions.quadrant2 == analyse.enemy_buildings_positions().positions(MinimapQuadrant(2)):
            print("Position of buildings in quadrant2 is [OK]")
        else:
            raise RuntimeError(
                "Expect the following buildings position for Q2 " + str(case.positions.quadrant2) + " and not " + str(
                    analyse.enemy_buildings_positions().positions(MinimapQuadrant(2)))
            )
        if case.positions.quadrant3 == analyse.enemy_buildings_positions().positions(MinimapQuadrant(3)):
            print("Position of buildings in quadrant3 is [OK]")
        else:
            raise RuntimeError(
                "Expect the following buildings position for Q3 " + str(case.positions.quadrant3) + " and not " + str(
                    analyse.enemy_buildings_positions().positions(MinimapQuadrant(3)))
            )
        print("Done\n")
