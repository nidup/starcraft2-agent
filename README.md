Starcraft2 Nidup's agents
=========================

Discovering PySC2 - StarCraft II Learning Environment, playing with reinforcement learning 🤖

Can be installed following [this doc](doc/install.md)

Notes
-----

These agents have been built to work properly on the Simple64 map, as a Terran player, and are not robust enough to play elsewhere.

Infinite Scouting Agent (Scripted)
----------------------------------

```
$ python3.6 -m pysc2.bin.agent --map Simple64 --agent nidup.pysc2.agents.ScoutingAgent --agent_race T
```

Build Order Agent (Scripted)
----------------------------

```
$ python3.6 -m pysc2.bin.agent --map Simple64 --agent nidup.pysc2.agents.BuildOrderAgent --agent_race T
```

Reinforcement Marine Agent (Machine Learning)
---------------------------------------------

**Explanation**

This agent is formerly [based on these tutorials](https://itnext.io/build-a-sparse-reward-pysc2-agent-a44e94ba5255)

It uses QLearning table on a reduced set of actions, build supply depot, barrack, train marine, attack on part of the map.

It has been fine tuned to be trained faster and win more games against the built-in AI.

**Train**

Train the agent by playing a lot of games:
```
$ python3.6 -m pysc2.bin.agent --map Simple64 --agent nidup.pysc2.agents.ReinforcementMarineAgent --agent_race T --norender --max_agent_steps=1000000
```

The option `--norender` can be added to disable the rendering and play game faster.

The option `--max_agent_steps` can be added to make the agent play longer. The default value is 2500.

On my laptop, with no render, running on CPU,
 - 100k agent steps ~= 30 episodes ~= 30 minutes
 - 400k agent steps ~= 144 episodes ~= 100 minutes

**Run**

After the reinforcement, you can run it:

```
$ python3.6 -m pysc2.bin.agent --map Simple64 --agent nidup.pysc2.agents.ReinforcementMarineAgent --agent_race T
```

**Data & Analysis**

*Game Results*

The game results are stored in `data` folder using a different file per agent.
The file is suffixed by `_results` and contains a pandas DataFrame.

*QLearning Table*

The reward history and final QLearning Table are stored in `data` folder using a different file per agent.
The file is suffixed by `_qlearning` and contains a pandas DataFrame.
This archive is re-used when it exists, you can drop it to train the agent from scratch.

*Report & queries*

Generate the learning report graph:
```
$ python3.6 generate_report.py --agent-name nidup.pysc2.agents.ReinforcementMarineAgent
```

Query the game results:
```
$ python3.6 generate_report.py --agent-name nidup.pysc2.agents.ReinforcementMarineAgent --filter win
```

*Evolution*

Attacking 4 quadrants:

![Image of ReinforcementMarineAgent 1](doc/ReinforcementMarineAgent_4quadrants.png)

Attacking 3 quadrants (not player's base quadrant):

![Image of ReinforcementMarineAgent 2](doc/ReinforcementMarineAgent_excludingplayerbase.png)

Attacking only enemy quadrant:

![Image of ReinforcementMarineAgent 3](doc/ReinforcementMarineAgent_enemyb1.png)

Attacking only enemy base 1 and base 2 quadrants:

![Image of ReinforcementMarineAgent 4](doc/ReinforcementMarineAgent_enemyb1andb2.png)

Credits
-------

Thank you @skjb for the following [tutorial](https://github.com/skjb/pysc2-tutorial) 🚀
