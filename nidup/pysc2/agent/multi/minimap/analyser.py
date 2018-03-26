
import math
from nidup.pysc2.agent.information import Location
from nidup.pysc2.wrapper.observations import Observations

_PLAYER_ENEMY = 4


class MinimapStringCleaner:

    def remove_one_cell_orphans(self, horizontal_string: str) -> str:
        search = "010"
        replace = "000"
        cleaned_string = self._remove_horizontal_orphans(horizontal_string, search, replace)
        cleaned_string = self._remove_vertical_orphans(cleaned_string, search, replace)
        return cleaned_string

    def remove_two_cells_orphans(self, horizontal_string: str) -> str:
        search = "0110"
        replace = "0000"
        cleaned_string = self._remove_horizontal_orphans(horizontal_string, search, replace)
        cleaned_string = self._remove_vertical_orphans(cleaned_string, search, replace)
        return cleaned_string

    def _remove_horizontal_orphans(self, horizontal_string: str, search: str, replace: str) -> str:
        cleaned_string = horizontal_string.replace(search, replace)
        cleaned_string = cleaned_string.replace(search, replace) # weird hack some are not cleaned up on first
        return cleaned_string

    def _remove_vertical_orphans(self, horizontal_string: str, search: str, replace: str) -> str:
        # switch to vertical and clean orphans
        horizontal_lines = []
        for row in horizontal_string.split("\n"):
            line = []
            for cell in list(row):
                line.append(cell)
            horizontal_lines.append(line)
        vertical_string = ""
        for column in range(0, 64):
            for line in range(0, 64):
                vertical_string = vertical_string + horizontal_lines[line][column]
            vertical_string = vertical_string + "\n"
        cleaned_vertical_string = vertical_string.replace(search, replace)
        # switch back to horizontal once cleaned
        vertical_lines = []
        for row in cleaned_vertical_string.split("\n"):
            line = []
            for cell in list(row):
                line.append(cell)
            vertical_lines.append(line)
        cleaned_horizontal_string = ""
        for column in range(0, 64):
            for line in range(0, 64):
                cleaned_horizontal_string = cleaned_horizontal_string + vertical_lines[line][column]
            cleaned_horizontal_string = cleaned_horizontal_string + "\n"
        return cleaned_horizontal_string


# 64x64 heat map view displaying all visible enemy in minimap
class MinimapAllEnemies:

    def __init__(self, enemies: []):
        self.enemies = enemies

    def all(self) -> []:
        return self.enemies

    def __str__(self):
        view = ""
        for row in self.enemies:
            for cell in row:
                view = view + str(cell)
            view = view + "\n"
        return view


# 64x64 heat map view displaying visible enemy's buildings in minimap (remove alone unit, under 2x2)
class MinimapOnlyEnemiesBuildings:

    def __init__(self, all_enemies: MinimapAllEnemies):
        all_enemies_string = str(all_enemies)
        only_building_string = MinimapStringCleaner().remove_one_cell_orphans(all_enemies_string)
        self.enemies = []
        for row in only_building_string.split("\n"):
            line = []
            for cell in list(row):
                line.append(int(cell))
            self.enemies.append(line)
        self.count_buildings = self._count(only_building_string)

    def _count(self, only_building_string: str) -> int:
        count_buildings = 0
        count_buildings_string = only_building_string
        if only_building_string.count("111") > 0:
            count_buildings = count_buildings_string.count("111") / 3
            count_buildings_string = count_buildings_string.replace("111", "000")
        if count_buildings_string.count("11") > 0:
            count_buildings = count_buildings + count_buildings_string.count("11") / 2
        count_buildings = math.ceil(count_buildings)
        return count_buildings

    def buildings(self) -> []:
        return self.enemies

    def __str__(self):
        view = ""
        for row in self.enemies:
            for cell in row:
                view = view + str(cell)
            view = view + "\n"
        return view

    def count(self):
        return self.count_buildings


# 64x64 heat map view displaying visible enemy's buildings in minimap (remove alone unit, under 3x3)
class MinimapOnlyEnemiesMainBasesBuildings:

    def __init__(self, enemies_buildings: MinimapOnlyEnemiesBuildings):
        enemies_buildings_string = str(enemies_buildings)
        main_buildings_string = MinimapStringCleaner().remove_two_cells_orphans(enemies_buildings_string)
        self.enemies = []
        for row in main_buildings_string.split("\n"):
            line = []
            for cell in list(row):
                line.append(int(cell))
            self.enemies.append(line)

        self.count_buildings = 0
        count_buildings = main_buildings_string
        if main_buildings_string.count("111") > 0:
            self.count_buildings = count_buildings.count("111") / 3
            self.count_buildings = math.ceil(self.count_buildings)

    def __str__(self):
        view = ""
        for row in self.enemies:
            for cell in row:
                view = view + str(cell)
            view = view + "\n"
        return view

    def count(self):
        return self.count_buildings


# Quadrant value object
class MinimapQuadrant:

    def __init__(self, index: int):
        self.index = index
        if index < 0 or index > 4:
            raise RuntimeError("Only 4 quadrants per minimap, from 1 to 4 ("+str(index)+" provided)")

    def code(self) -> int:
        return self.index


# Provides enemy's buildings positions on the designated minimap quadrant
class MinimapEnemyBuildingsPositions:

    def __init__(self, enemy_buildings: MinimapOnlyEnemiesBuildings):
        self.enemy_buildings = enemy_buildings

    # returns [[x1, y1], [x2, y2]]
    def positions(self, quadrant: MinimapQuadrant) -> []:
        building_positions = []
        for line in range(0, 64):
            for column in range(0, 64):
                if self.enemy_buildings.buildings()[line][column] == 1:
                    if quadrant.code() == 1 and column < 32 and line < 32:
                        building_positions.append([column, line])
                    elif quadrant.code() == 2 and column >= 32 and line < 32:
                        building_positions.append([column, line])
                    elif quadrant.code() == 3 and column < 32 and line >= 32:
                        building_positions.append([column, line])
                    elif quadrant.code() == 4 and column >= 32 and line >= 32:
                        building_positions.append([column, line])

        #print(self.enemy_buildings.buildings())
        #print(building_positions)
        #exit(-1)

        return building_positions


# Provides all enemy's positions on the designated minimap quadrant
class MinimapAllEnemyPositions:

    def __init__(self, all_enemies: MinimapAllEnemies):
        self.enemies = all_enemies

    # returns [[x1, y1], [x2, y2]]
    def positions(self, quadrant: MinimapQuadrant) -> []:
        positions = []
        for line in range(0, 64):
            for column in range(0, 64):
                if self.enemies.all()[line][column] == 1:
                    if quadrant.code() == 1 and column < 32 and line < 32:
                        positions.append([column, line])
                    elif quadrant.code() == 2 and column >= 32 and line < 32:
                        positions.append([column, line])
                    elif quadrant.code() == 3 and column < 32 and line >= 32:
                        positions.append([column, line])
                    elif quadrant.code() == 4 and column >= 32 and line >= 32:
                        positions.append([column, line])
        return positions


# Analyse minimap providing several heat map views
class MinimapEnemyAnalyse:

    def __init__(self, enemy_y: [], enemy_x: []):
        enemy_minimap = self._build_minimap(enemy_y, enemy_x)
        self.all_enemies_view = MinimapAllEnemies(enemy_minimap)
        self.all_buildings_view = MinimapOnlyEnemiesBuildings(self.all_enemies_view)
        self.main_buildings_view = MinimapOnlyEnemiesMainBasesBuildings(self.all_buildings_view)
        self.buildings_positions = MinimapEnemyBuildingsPositions(self.all_buildings_view)
        self.all_positions = MinimapAllEnemyPositions(self.all_enemies_view)

    def _build_minimap(self, enemy_y: [], enemy_x: []) -> []:
        enemy_minimap = []
        for y in range(0, 64):
            enemy_minimap.append([])
            for x in range(0, 64):
                enemy_minimap[y].append(0)
        for visible_enemy in range(0, len(enemy_y)):
            enemy_minimap[enemy_y[visible_enemy]][enemy_x[visible_enemy]] = 1
        return enemy_minimap

    def all_enemies(self) -> MinimapAllEnemies:
        return self.all_enemies_view

    def all_enemies_building(self) -> MinimapOnlyEnemiesBuildings:
        return self.all_buildings_view

    def all_enemies_main_buildings(self) -> MinimapOnlyEnemiesMainBasesBuildings:
        return self.main_buildings_view

    def enemy_buildings_positions(self) -> MinimapEnemyBuildingsPositions:
        return self.buildings_positions

    def all_enemy_positions(self) -> MinimapAllEnemyPositions:
        return self.all_positions


# Minimap is a 64x64 view of the game
class MinimapAnalyser:

    def analyse(self, observations: Observations, location: Location) -> MinimapEnemyAnalyse:
        enemy_y, enemy_x = (observations.minimap().player_relative() == _PLAYER_ENEMY).nonzero()
        #print(enemy_y)
        #print(enemy_x)
        analyse = MinimapEnemyAnalyse(enemy_y, enemy_x)
        #print(analyse.all_enemies())
        return analyse
