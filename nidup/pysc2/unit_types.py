
# Unit IDs cf https://github.com/Blizzard/s2client-api/blob/master/include/sc2api/sc2_typeenums.h
_TERRAN_COMMANDCENTER = 18
_TERRAN_SUPPLYDEPOT = 19
_TERRAN_REFINERY = 20
_TERRAN_BARRACKS = 21
_TERRAN_FACTORY = 27
_TERRAN_SCV = 45
_TERRAN_ORBITALCOMMAND = 132
_NEUTRAL_MINERALFIELD = 341
_NEUTRAL_VESPENE_GEYSER = 342


class UnitTypeIds:

    def neutral_vespene_geyser(self) -> int:
        return _NEUTRAL_VESPENE_GEYSER

    def terran_barracks(self) -> int:
        return _TERRAN_BARRACKS

    def terran_command_center(self) -> int:
        return _TERRAN_COMMANDCENTER

    def terran_orbital_command(self) -> int:
        return _TERRAN_ORBITALCOMMAND

    def terran_factory(self) -> int:
        return _TERRAN_FACTORY

    def terran_scv(self) -> int:
        return _TERRAN_SCV

    def terran_refinery(self) -> int:
        return _TERRAN_REFINERY
