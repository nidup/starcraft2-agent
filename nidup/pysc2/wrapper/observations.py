
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


class ScoreDetails:

    def __init__(self, obs_score):
        self.obs_score = obs_score

    def score(self) -> int:
        return self.obs_score[0]

    def idle_production_time(self) -> int:
        return self.obs_score[1]

    def idle_worker_time(self) -> int:
        return self.obs_score[2]

    def total_value_units(self) -> int:
        return self.obs_score[3]

    def total_value_structures(self) -> int:
        return self.obs_score[4]

    def killed_value_units(self) -> int:
        return self.obs_score[5]

    def killed_value_structures(self) -> int:
        return self.obs_score[6]

    def collected_minerals(self) -> int:
        return self.obs_score[7]

    def collected_vespene(self) -> int:
        return self.obs_score[8]

    def collection_rate_minerals(self) -> int:
        return self.obs_score[9]

    def collection_rate_vespene(self) -> int:
        return self.obs_score[10]

    def spent_minerals(self) -> int:
        return self.obs_score[11]

    def spent_vespene(self) -> int:
        return self.obs_score[12]


class SingleSelect:

    def __init__(self, select):
        self.select = select

    def empty(self) -> bool:
        return len(self.select) == 0

    def unit_type(self) -> int:
        return self.select[0][0]

    def player_relative(self) -> int:
        return self.select[0][1]

    def health(self) -> int:
        return self.select[0][2]

    def shields(self) -> int:
        return self.select[0][3]

    def energy(self) -> int:
        return self.select[0][4]

    def transport_slot_taken(self) -> int:
        return self.select[0][5]

    def build_progress_percentage(self) -> int:
        return self.select[0][6]

    def is_built(self) -> bool:
        return self.build_progress_percentage() == 0


class MultiSelect:

    def __init__(self, select):
        self.select = select

    def empty(self) -> bool:
        return len(self.select) == 0

    def unit_type(self, index: int) -> int:
        return self.select[index][0]

    def player_relative(self, index: int) -> int:
        return self.select[index][1]

    def health(self, index: int) -> int:
        return self.select[index][2]

    def shields(self, index: int) -> int:
        return self.select[index][3]

    def energy(self, index: int) -> int:
        return self.select[index][4]

    def transport_slot_taken(self, index: int) -> int:
        return self.select[index][5]

    def build_progress_percentage(self, index: int) -> int:
        return self.select[index][6]

    def is_built(self, index: int) -> bool:
        return self.build_progress_percentage(index) == 0


# Wrap `obs` variable, a series of nested arrays to an object
# cf https://github.com/deepmind/pysc2/blob/master/docs/environment.md
class Observations:

    def __init__(self, obs):
        self.screen_features = ScreenFeatures(obs.observation["screen"])
        self.player_information = PlayerInformation(obs.observation["player"])
        self.minimap_features = MinimapFeatures(obs.observation["minimap"])
        self.available_actions_data = obs.observation["available_actions"]
        self.control_groups_data = obs.observation["control_groups"]
        self.single_select_data = SingleSelect(obs.observation["single_select"])
        self.multi_select_data = MultiSelect(obs.observation["multi_select"])
        self.first_data = obs.first()
        self.last_data = obs.last()
        self.reward_data = obs.reward
        self.score_details = ScoreDetails(obs.observation["score_cumulative"])

    def first(self) -> bool:
        return self.first_data

    def last(self) -> bool:
        return self.last_data

    def player(self) -> PlayerInformation:
        return self.player_information

    def screen(self) -> ScreenFeatures:
        return self.screen_features

    def minimap(self) -> MinimapFeatures:
        return self.minimap_features

    def available_actions(self):
        return self.available_actions_data

    def control_groups(self):
        return self.control_groups_data

    def single_select(self) -> SingleSelect:
        return self.single_select_data

    def multi_select(self) -> MultiSelect:
        return self.multi_select_data

    def reward(self) -> int:
        return self.reward_data

    def score_cumulative(self) -> ScoreDetails:
        return self.score_details
