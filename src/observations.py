

# Wrap `obs` variable, a series of nested arrays to an object
# cf https://github.com/deepmind/pysc2/blob/master/docs/environment.md
class Observations:

    obs = None

    def __init__(self, obs):
        self.obs = obs

    def player(self):
        return self.obs.observation["player"]

    def screen(self):
        return self.obs.observation["screen"]

    def available_actions(self):
        return self.obs.observation["available_actions"]

    def minimap(self):
        return self.obs.observation["minimap"]
