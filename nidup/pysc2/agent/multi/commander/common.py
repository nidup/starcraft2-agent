

class TrainActionsCodes:

    def do_nothing(self) -> str:
        return 'donothing'

    def train_marine(self) -> str:
        return 'trainmarine'

    def train_marauder(self) -> str:
        return 'trainmarauder'

    def train_hellion(self) -> str:
        return 'trainhellion'

    def train_medivac(self) -> str:
        return 'trainmedivac'


class TrainActionsSet:

    def __init__(self, code: str, action_codes: []):
        self.code_data = code
        self.actions_codes_arr = action_codes

    def code(self) -> str:
        return self.code_data

    def actions(self) -> []:
        return self.actions_codes_arr


class TrainActionsSetRegistry:

    def __init__(self):
        self.sets = [
            TrainActionsSet(
                "MM",
                [
                    TrainActionsCodes().do_nothing(),
                    TrainActionsCodes().train_marine(),
                    TrainActionsCodes().train_marauder(),
                ]
            ),
            TrainActionsSet(
                "MMM",
                [
                    TrainActionsCodes().do_nothing(),
                    TrainActionsCodes().train_marine(),
                    TrainActionsCodes().train_marauder(),
                    TrainActionsCodes().train_medivac()
                ]
            ),
            TrainActionsSet(
                "MH",
                [
                    TrainActionsCodes().do_nothing(),
                    TrainActionsCodes().train_marine(),
                    TrainActionsCodes().train_hellion(),
                ]
            )
        ]

    def actions_set(self, code) -> TrainActionsSet:
        for a_set in self.sets:
            if a_set.code() == code:
                return a_set
        raise AttributeError("Unknown ActionSet " + code)
