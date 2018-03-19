
from pysc2.lib import actions

_ATTACK_MINIMAP = actions.FUNCTIONS.Attack_minimap.id
_ATTACK_SCREEN = actions.FUNCTIONS.Attack_screen.id
_BUILD_SUPPLYDEPOT = actions.FUNCTIONS.Build_SupplyDepot_screen.id
_BUILD_BARRACKS = actions.FUNCTIONS.Build_Barracks_screen.id
_BUILD_TECHLAB_BARRACKS = actions.FUNCTIONS.Build_TechLab_screen.id
_BUILD_REACTOR_BARRACKS = actions.FUNCTIONS.Build_Reactor_screen.id
_BUILD_REFINERY = actions.FUNCTIONS.Build_Refinery_screen.id
_BUILD_FACTORY = actions.FUNCTIONS.Build_Factory_screen.id
_BUILD_STARPORT = actions.FUNCTIONS.Build_Starport_screen.id
_HARVEST_GATHER = actions.FUNCTIONS.Harvest_Gather_screen.id
_MORPH_ORBITAL_COMMAND = actions.FUNCTIONS.Morph_OrbitalCommand_quick.id
_MOVE_MINIMAP = actions.FUNCTIONS.Move_minimap.id
_MOVE_SCREEN = actions.FUNCTIONS.Move_screen.id
_MOVE_CAMERA = actions.FUNCTIONS.move_camera.id
_NOOP = actions.FUNCTIONS.no_op.id
_RALLY_UNITS_MINIMAP = actions.FUNCTIONS.Rally_Units_minimap.id
_RESEARCH_COMBAT_SHIELD = actions.FUNCTIONS.Research_CombatShield_quick.id
_RESEARCH_CONCUSSIVE_SHELLS = actions.FUNCTIONS.Research_ConcussiveShells_quick.id
_SELECT_POINT = actions.FUNCTIONS.select_point.id
_SELECT_IDLE_WORKER = actions.FUNCTIONS.select_idle_worker.id
_SELECT_ARMY = actions.FUNCTIONS.select_army.id
_SELECT_UNIT = actions.FUNCTIONS.select_unit.id
_SELECT_RECT = actions.FUNCTIONS.select_rect.id
_SELECT_CONTROL_GROUP = actions.FUNCTIONS.select_control_group.id
_TRAIN_MARINE = actions.FUNCTIONS.Train_Marine_quick.id
_TRAIN_MARAUDER = actions.FUNCTIONS.Train_Marauder_quick.id
_TRAIN_MEDIVAC = actions.FUNCTIONS.Train_Medivac_quick.id
_TRAIN_SCV = actions.FUNCTIONS.Train_SCV_quick.id
_TRAIN_HELLION = actions.FUNCTIONS.Train_Hellion_quick.id


_NOT_QUEUED = [0]
_QUEUED = [1]
_SELECT_ALL = [2]


class TerranActionIds:

    def attack_minimap(self) -> int:
        return _ATTACK_MINIMAP

    def build_barracks(self) -> int:
        return _BUILD_BARRACKS

    def build_factory(self) -> int:
        return _BUILD_FACTORY

    def build_refinery(self) -> int:
        return _BUILD_REFINERY

    def build_starport(self) -> int:
        return _BUILD_STARPORT

    def build_supply_depot(self) -> int:
        return _BUILD_SUPPLYDEPOT

    def build_techlab_barracks(self) -> int:
        return _BUILD_TECHLAB_BARRACKS

    def build_reactor_barracks(self) -> int:
        return _BUILD_REACTOR_BARRACKS

    def harvest_gather(self) -> int:
        return _HARVEST_GATHER

    def move_camera(self) -> int:
        return _MOVE_CAMERA

    def move_minimap(self) -> int:
        return _MOVE_MINIMAP

    def move_screen(self) -> int:
        return _MOVE_SCREEN

    def morph_orbital_command(self) -> int:
        return _MORPH_ORBITAL_COMMAND

    def no_op(self) -> int:
        return _NOOP

    def rally_units_minimap(self) -> int:
        return _RALLY_UNITS_MINIMAP

    def research_combat_shield(self) -> int:
        return _RESEARCH_COMBAT_SHIELD

    def research_concussive_shells(self) -> int:
        return _RESEARCH_CONCUSSIVE_SHELLS

    def select_army(self) -> int:
        return _SELECT_ARMY

    def select_control_group(self) -> int:
        return _SELECT_CONTROL_GROUP

    def select_unit(self) -> int:
        return _SELECT_UNIT

    def train_hellion(self) -> int:
        return _TRAIN_HELLION

    def train_marine(self) -> int:
        return _TRAIN_MARINE

    def train_marauder(self) -> int:
        return _TRAIN_MARAUDER

    def train_medivac(self) -> int:
        return _TRAIN_MEDIVAC

    def train_scv(self) -> int:
        return _TRAIN_SCV


class ActionQueueParameter:

    def queued(self) -> []:
        return _QUEUED

    def not_queued(self) -> []:
        return _NOT_QUEUED


class TerranActions:

    def attack_minimap(self, target) -> actions.FunctionCall:
        return actions.FunctionCall(_ATTACK_MINIMAP, [_NOT_QUEUED, target])

    def build_barracks(self, target) -> actions.FunctionCall:
        return actions.FunctionCall(_BUILD_BARRACKS, [_NOT_QUEUED, target])

    def build_factory(self, target) -> actions.FunctionCall:
        return actions.FunctionCall(_BUILD_FACTORY, [_NOT_QUEUED, target])

    def build_refinery(self, target) -> actions.FunctionCall:
        return actions.FunctionCall(_BUILD_REFINERY, [_NOT_QUEUED, target])

    def build_supply_depot(self, target) -> actions.FunctionCall:
        return actions.FunctionCall(_BUILD_SUPPLYDEPOT, [_NOT_QUEUED, target])

    def build_starport(self, target) -> actions.FunctionCall:
        return actions.FunctionCall(_BUILD_STARPORT, [_NOT_QUEUED, target])

    def build_techlab_barracks(self, target) -> actions.FunctionCall:
        return actions.FunctionCall(_BUILD_TECHLAB_BARRACKS, [_NOT_QUEUED, target])

    def build_reactor_barracks(self, target) -> actions.FunctionCall:
        return actions.FunctionCall(_BUILD_REACTOR_BARRACKS, [_NOT_QUEUED, target])

    def harvest_gather(self, target) -> actions.FunctionCall:
        return actions.FunctionCall(_HARVEST_GATHER, [_QUEUED, target])

    def move_camera(self, target) -> actions.FunctionCall:
        return actions.FunctionCall(_MOVE_CAMERA, [target])

    def move_minimap(self, target: [], queued: [] = _NOT_QUEUED) -> actions.FunctionCall:
        return actions.FunctionCall(_MOVE_MINIMAP, [queued, target])

    def move_screen(self, target) -> actions.FunctionCall:
        return actions.FunctionCall(_MOVE_SCREEN, [_NOT_QUEUED, target])

    def morph_orbital_command(self) -> actions.FunctionCall:
        return actions.FunctionCall(_MORPH_ORBITAL_COMMAND, [_NOT_QUEUED])

    def no_op(self) -> actions.FunctionCall:
        return actions.FunctionCall(_NOOP, [])

    def rally_units_minimap(self, target) -> actions.FunctionCall:
        return actions.FunctionCall(_RALLY_UNITS_MINIMAP, [_NOT_QUEUED, target])

    def research_combat_shield(self) -> actions.FunctionCall:
        return actions.FunctionCall(_RESEARCH_COMBAT_SHIELD, [_NOT_QUEUED])

    def research_concussive_shells(self) -> actions.FunctionCall:
        return actions.FunctionCall(_RESEARCH_CONCUSSIVE_SHELLS, [_NOT_QUEUED])

    def select_army(self) -> actions.FunctionCall:
        return actions.FunctionCall(_SELECT_ARMY, [_NOT_QUEUED])

    def select_control_group(self, group_id) -> actions.FunctionCall:
        return self._select_control_group(0, group_id)

    def set_control_group(self, group_id) -> actions.FunctionCall:
        return self._select_control_group(1, group_id)

    def add_control_group(self, group_id) -> actions.FunctionCall:
        return self._select_control_group(2, group_id)

    # group_actions are detailled here https://github.com/deepmind/pysc2/issues/39#issuecomment-323156798
    def _select_control_group(self, group_action, group_id) -> actions.FunctionCall:
        return actions.FunctionCall(_SELECT_CONTROL_GROUP, [[group_action], [group_id]])

    def select_idle_worker(self) -> actions.FunctionCall:
        return actions.FunctionCall(_SELECT_IDLE_WORKER, [_NOT_QUEUED])

    def select_point(self, target) -> actions.FunctionCall:
        return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])

    def select_point_all(self, target) -> actions.FunctionCall:
        return actions.FunctionCall(_SELECT_POINT, [_SELECT_ALL, target])

    def select_rect(self, point1, point2) -> actions.FunctionCall:
        return actions.FunctionCall(_SELECT_RECT, [_NOT_QUEUED, point1, point2])

    # more information here https://github.com/deepmind/pysc2/issues/60
    def select_unit(self, unit_index):
        return actions.FunctionCall(_SELECT_UNIT, [[0], [unit_index]])

    def select_all_units(self, unit_index):
        return actions.FunctionCall(_SELECT_UNIT, [[1], [unit_index]])

    def train_hellion(self) -> actions.FunctionCall:
        return actions.FunctionCall(_TRAIN_HELLION, [_QUEUED])

    def train_marine(self) -> actions.FunctionCall:
        return actions.FunctionCall(_TRAIN_MARINE, [_QUEUED])

    def train_marauder(self) -> actions.FunctionCall:
        return actions.FunctionCall(_TRAIN_MARAUDER, [_QUEUED])

    def train_scv(self) -> actions.FunctionCall:
        return actions.FunctionCall(_TRAIN_SCV, [_NOT_QUEUED])

    def train_medivac(self) -> int:
        return actions.FunctionCall(_TRAIN_MEDIVAC, [_NOT_QUEUED])
