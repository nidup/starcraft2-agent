Reinforcement Marine Agent (Machine Learning)
=============================================

Explanation
-----------

This agent is formerly [based on these tutorials](https://itnext.io/build-a-sparse-reward-pysc2-agent-a44e94ba5255)

It uses QLearning table on a reduced set of actions, build supply depot, barrack, train marine, attack on part of the map.

The map is split in 4 quadrant that can be attacked, so we have 4 attack actions.

When targeting a quadrant, 9 different points can be attacked, the point is selected randomly.

The agent's training is reinforced using a sparse reward applied on actions depending on the result of an episode.

It has been fine tuned to be trained faster and win more games against the built-in AI.

Train
-----

Train the agent by playing a lot of games:
```
$ python3.6 -m pysc2.bin.agent --map Simple64 --agent nidup.pysc2.agents.ReinforcementMarineAgent --agent_race T --norender --max_agent_steps=1000000
```

The option `--norender` can be added to disable the rendering and play game faster.

The option `--max_agent_steps` can be added to make the agent play longer. The default value is 2500.

On my laptop, with no render, running on CPU,
 - 100k agent steps ~= 30 episodes ~= 30 minutes
 - 400k agent steps ~= 144 episodes ~= 100 minutes

The reward history and final Q-Learning Table are stored in `data` folder using a different file per agent.
The file is suffixed by `_QLearning` and contains a pandas DataFrame.
This archive is re-used when it exists, you can drop it to train the agent from scratch.

Run
---

After the reinforcement, you can run it:

```
$ python3.6 -m pysc2.bin.agent --map Simple64 --agent nidup.pysc2.agents.ReinforcementMarineAgent --agent_race T
```

Evolution
---------

Attacking 4 quadrants:

![Image of ReinforcementMarineAgent 1](ReinforcementMarineAgent_4quadrants.png)

Attacking 3 quadrants (not player's base quadrant):

![Image of ReinforcementMarineAgent 2](ReinforcementMarineAgent_excludingplayerbase.png)

Attacking only enemy quadrant:

![Image of ReinforcementMarineAgent 3](ReinforcementMarineAgent_enemyb1.png)

Attacking only enemy base 1 and base 2 quadrants:

![Image of ReinforcementMarineAgent 4](ReinforcementMarineAgent_enemyb1andb2.png)
