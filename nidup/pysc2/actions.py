
from pysc2.lib import actions

_ATTACK_MINIMAP = actions.FUNCTIONS.Attack_minimap.id
_ATTACK_SCREEN = actions.FUNCTIONS.Attack_screen.id
_BUILD_SUPPLYDEPOT = actions.FUNCTIONS.Build_SupplyDepot_screen.id
_BUILD_BARRACKS = actions.FUNCTIONS.Build_Barracks_screen.id
_BUILD_TECHLAB_BARRACKS = actions.FUNCTIONS.Build_TechLab_screen.id
_BUILD_REFINERY = actions.FUNCTIONS.Build_Refinery_screen.id
_BUILD_FACTORY = actions.FUNCTIONS.Build_Factory_screen.id
_MORPH_ORBITAL_COMMAND = actions.FUNCTIONS.Morph_OrbitalCommand_quick.id
_MOVE_MINIMAP = actions.FUNCTIONS.Move_minimap.id
_MOVE_SCREEN = actions.FUNCTIONS.Move_screen.id
_NOOP = actions.FUNCTIONS.no_op.id
_RALLY_UNITS_MINIMAP = actions.FUNCTIONS.Rally_Units_minimap.id
_SELECT_POINT = actions.FUNCTIONS.select_point.id
_SELECT_IDLE_WORKER = actions.FUNCTIONS.select_idle_worker.id
_SELECT_ARMY = actions.FUNCTIONS.select_army.id
_SELECT_UNIT = actions.FUNCTIONS.select_unit.id
_SELECT_CONTROL_GROUP = actions.FUNCTIONS.select_control_group.id
_TRAIN_MARINE = actions.FUNCTIONS.Train_Marine_quick.id
_TRAIN_MARAUDER = actions.FUNCTIONS.Train_Marauder_quick.id


_NOT_QUEUED = [0]
_QUEUED = [1]


class TerranActionIds:

    def attack_minimap(self) -> int:
        return _ATTACK_MINIMAP

    def build_barracks(self) -> int:
        return _BUILD_BARRACKS

    def build_factory(self) -> int:
        return _BUILD_FACTORY

    def build_refinery(self) -> int:
        return _BUILD_REFINERY

    def build_supply_depot(self) -> int:
        return _BUILD_SUPPLYDEPOT

    def build_techlab_barracks(self) -> int:
        return _BUILD_TECHLAB_BARRACKS

    def move_minimap(self) -> int:
        return _MOVE_MINIMAP

    def move_screen(self) -> int:
        return _MOVE_SCREEN

    def morph_orbital_command(self) -> int:
        return _MORPH_ORBITAL_COMMAND

    def no_op(self) -> int:
        return _NOOP

    def select_army(self) -> int:
        return _SELECT_ARMY

    def train_marine(self) -> int:
        return _TRAIN_MARINE

    def train_marauder(self) -> int:
        return _TRAIN_MARAUDER


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

    def build_techlab_barracks(self, target) -> actions.FunctionCall:
        return actions.FunctionCall(_BUILD_TECHLAB_BARRACKS, [_NOT_QUEUED, target])

    def move_minimap(self, target) -> actions.FunctionCall:
        return actions.FunctionCall(_MOVE_MINIMAP, [_NOT_QUEUED, target])

    def move_screen(self, target) -> actions.FunctionCall:
        return actions.FunctionCall(_MOVE_SCREEN, [_NOT_QUEUED, target])

    def morph_orbital_command(self) -> actions.FunctionCall:
        return actions.FunctionCall(_MORPH_ORBITAL_COMMAND, [_NOT_QUEUED])

    def no_op(self) -> actions.FunctionCall:
        return actions.FunctionCall(_NOOP, [])

    def rally_units_minimap(self, target) -> actions.FunctionCall:
        return actions.FunctionCall(_RALLY_UNITS_MINIMAP, [_NOT_QUEUED, target])

    def select_army(self) -> actions.FunctionCall:
        return actions.FunctionCall(_SELECT_ARMY, [_NOT_QUEUED])

    def select_idle_worker(self) -> actions.FunctionCall:
        return actions.FunctionCall(_SELECT_IDLE_WORKER, [_NOT_QUEUED])

    def select_point(self, target) -> actions.FunctionCall:
        return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])

    def train_marine(self) -> actions.FunctionCall:
        return actions.FunctionCall(_TRAIN_MARINE, [_NOT_QUEUED])

    def train_marauder(self) -> actions.FunctionCall:
        return actions.FunctionCall(_TRAIN_MARAUDER, [_NOT_QUEUED])
