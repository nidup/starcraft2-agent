
from nidup.pysc2.agent.multi.minimap.analyser import MinimapEnemyAnalyse


class Expectations:
    def __init__(self, bases: int, buildings: int):
        self.bases = bases
        self.buildings = buildings


class MinimapCase:

    def __init__(self, description: str, enemy_y: [], enemy_x: [], expectations: Expectations):
        self.enemy_y = enemy_y
        self.enemy_x = enemy_x
        self.description = description
        self.expectations = expectations


if __name__ == '__main__':

    cases = [
        MinimapCase(
            "playing top left, expecting an enemy's base in bottom right",
            [44, 44, 44, 45, 45, 45, 45, 45, 46, 46, 46, 46, 46, 47, 48, 49, 49, 49, 50, 50, 50],
            [38, 39, 40, 35, 36, 38, 39, 40, 35, 36, 38, 39, 40, 34, 32, 33, 37, 38, 34, 37, 38],
            Expectations(1, 3)
        ),
        MinimapCase(
            "playing top left, expecting an enemy's base in bottom right and a spread enemy's unit in the bottom left",
            [44, 44, 44, 45, 45, 45, 46, 46, 46, 46, 49, 49, 50, 50],
            [38, 39, 40, 38, 39, 40, 18, 38, 39, 40, 37, 38, 37, 38],
            Expectations(1, 2)
        ),
        MinimapCase(
            "playing top left, expecting 2 enemy's base and being under attack",
            [19, 20, 21, 22, 22, 23, 24, 43, 43, 44, 44, 44, 44, 44, 44, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 46,
             46, 46, 46, 46, 46, 46, 46, 46, 46, 47, 47, 47, 47, 47, 47, 48, 48, 48, 48, 48, 49, 49, 49, 49, 49, 49,
             50, 50, 50, 50, 50, 50, 52, 52, 52, 52, 53, 53, 53],
            [22, 25, 18, 23, 25, 25, 25, 33, 34, 28, 33, 34, 38, 39, 40, 11, 12, 25, 29, 30, 35, 36, 38, 39, 40, 11, 12,
             29, 30, 34, 35, 36, 38, 39, 40, 16, 17, 18, 34, 35, 36, 16, 17, 18, 35, 36, 16, 17, 18, 34, 37, 38, 17, 18,
             34, 35, 37, 38, 15, 18, 19, 20, 16, 19, 20],
            Expectations(2, 10)
        ),
        MinimapCase(
            "playing bottom right, expecting 2 enemy's base",
            [20, 20, 20, 21, 21, 21, 21, 21, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 23, 23, 23, 23, 23, 24, 24, 24,
             24, 25, 25, 26, 26, 39],
            [40, 41, 42, 22, 23, 40, 41, 42, 18, 19, 20, 22, 23, 25, 40, 41, 42, 45, 46, 18, 19, 20, 45, 46, 18, 19, 20,
             28, 22, 23, 22, 23, 44],
            Expectations(2, 5)
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
        print("Done\n")
