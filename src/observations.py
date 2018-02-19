
from pysc2.lib import features


class ScreenFeatures:
    obs_screen = None

    def __init__(self, obs_screen):
        self.obs_screen = obs_screen

    def height_map(self):
        return self.obs_screen[features.SCREEN_FEATURES.height_map.index]

    def visibility_map(self):
        return self.obs_screen[features.SCREEN_FEATURES.visibility_map.index]

    def creep(self):
        return self.obs_screen[features.SCREEN_FEATURES.creep.index]

    def power(self):
        return self.obs_screen[features.SCREEN_FEATURES.power.index]

    def player_id(self):
        return self.obs_screen[features.SCREEN_FEATURES.player_id.index]

    def player_relative(self):
        return self.obs_screen[features.SCREEN_FEATURES.player_relative.index]

    def unit_type(self):
        return self.obs_screen[features.SCREEN_FEATURES.unit_type.index]

    def selected(self):
        return self.obs_screen[features.SCREEN_FEATURES.selected.index]

    def unit_hit_points(self):
        return self.obs_screen[features.SCREEN_FEATURES.unit_hit_points.index]

    def unit_hit_points_ratio(self):
        return self.obs_screen[features.SCREEN_FEATURES.unit_hit_points_ratio.index]

    def unit_energy(self):
        return self.obs_screen[features.SCREEN_FEATURES.unit_energy.index]

    def unit_energy_ratio(self):
        return self.obs_screen[features.SCREEN_FEATURES.unit_energy_ratio.index]

    def unit_shields(self):
        return self.obs_screen[features.SCREEN_FEATURES.unit_shields.index]

    def unit_shields_ratio(self):
        return self.obs_screen[features.SCREEN_FEATURES.unit_shields_ratio.index]

    def unit_density(self):
        return self.obs_screen[features.SCREEN_FEATURES.unit_density.index]

    def unit_density_aa(self):
        return self.obs_screen[features.SCREEN_FEATURES.unit_density_aa.index]

    def effects(self):
        return self.obs_screen[features.SCREEN_FEATURES.effects.index]


class MinimapFeatures:
    obs_minimap = None

    def __init__(self, obs_minimap):
        self.obs_minimap = obs_minimap

    def height_map(self):
        return self.obs_minimap[features.MINIMAP_FEATURES.height_map.index]

    def visibility_map(self):
        return self.obs_minimap[features.MINIMAP_FEATURES.visibility_map.index]

    def creep(self):
        return self.obs_minimap[features.MINIMAP_FEATURES.creep.index]

    def camera(self):
        return self.obs_minimap[features.MINIMAP_FEATURES.camera.index]

    def player_id(self):
        return self.obs_minimap[features.MINIMAP_FEATURES.player_id.index]

    def player_relative(self):
        return self.obs_minimap[features.MINIMAP_FEATURES.player_relative.index]

    def selected(self):
        return self.obs_minimap[features.MINIMAP_FEATURES.selected.index]


class PlayerInformation:
    obs_player = None

    def __init__(self, obs_player):
        self.obs_player = obs_player

    def player_id(self):
        return self.obs_player[0]

    def minerals(self):
        return self.obs_player[1]

    def vespene(self):
        return self.obs_player[2]

    def food_used(self):
        return self.obs_player[3]

    def food_cap(self):
        return self.obs_player[4]

    def food_army(self):
        return self.obs_player[5]

    def food_workers(self):
        return self.obs_player[6]

    def idle_worker_count(self):
        return self.obs_player[7]

    def army_count(self):
        return self.obs_player[8]

    def warp_gate_count(self):
        return self.obs_player[9]

    def larva_count(self):
        return self.obs_player[10]


# Wrap `obs` variable, a series of nested arrays to an object
# cf https://github.com/deepmind/pysc2/blob/master/docs/environment.md
class Observations:

    obs = None
    screen_features: None
    player_information: None
    minimap_features: None

    def __init__(self, obs):
        self.obs = obs
        self.screen_features = ScreenFeatures(self.obs.observation["screen"])
        self.player_information = PlayerInformation(self.obs.observation["player"])
        self.minimap_features = MinimapFeatures(self.obs.observation["minimap"])

    def player(self) -> PlayerInformation:
        return self.player_information

    def screen(self) -> ScreenFeatures:
        return self.screen_features

    def available_actions(self):
        return self.obs.observation["available_actions"]

    def minimap(self) -> MinimapFeatures:
        return self.minimap_features

