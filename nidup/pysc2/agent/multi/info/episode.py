

class EpisodeDetails:

    def __init__(self):
        self.episode_step_index = 0

    def episode_step(self) -> int:
        return self.episode_step_index

    def increment_episode_step(self):
        self.episode_step_index = self.episode_step_index + 1

