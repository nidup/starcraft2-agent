Starcraft 2 agent
=================

Discovering PySC2 - StarCraft II Learning Environment, playing with simple agent and reinforcement learning 🤖

Clone the repository
--------------------

```
$ cd ~/git
$ git clone git@github.com:nidup/starcraft2-agent.git
$ cd ~/git/starcraft2-agent/
```

Install with Python 3.6
-----------------------

Install [PySC2 - StarCraft II Learning Environment](https://github.com/deepmind/pysc2)

```
$ python3.6 -m pip install setuptools
$ python3.6 -m pip install pysc2
$ python3.6 -m pip install scipy
$ python3.6 -m pip install sklearn
$ python3.6 -m pip install pandas
$ python3.6 -m pip install matplotlib
```

Download [Starcraft 2 Linux Package](https://github.com/Blizzard/s2client-proto#downloads) and extract into the expected default location:

```
$ cd ~/Downloads
$ unzip SC2.4.0.2.zip
$ mv ~/Downloads/StarCraftII ~/
```

Download the [mini games maps](https://github.com/deepmind/pysc2#get-the-maps) and [Map Packs](https://github.com/Blizzard/s2client-proto#downloads) and extract into the expected map location:

```
$ cd ~/Downloads
$ unzip mini_games.zip
$ unzip Melee.zip
$ unzip Ladder2017Season3.zip
$ mv ~/Downloads/mini_games ~/StarCraftII/Maps/
$ mv ~/Downloads/Melee ~/StarCraftII/Maps/
$ mv ~/Downloads/Ladder2017Season3 ~/StarCraftII/Maps/
```

Test the environment
--------------------

By playing a game as a human,

```
python3.6 -m pysc2.bin.play --map Simple64
```

More options and details can be found on [PySC2 - StarCraft II Learning Environment](https://github.com/deepmind/pysc2)

Run the PySC2 demo agents
-------------------------

Collect Minerals Mini Game,

```
$ python3.6 -m pysc2.bin.agent --map CollectMineralShards --agent pysc2.agents.scripted_agent.CollectMineralShards
```

Move To Beacon Mini Game,

```
$ python3.6 -m pysc2.bin.agent --map MoveToBeacon --agent pysc2.agents.scripted_agent.MoveToBeacon
```

Defeat Roaches Mini Game,

```
$ python3.6 -m pysc2.bin.agent --map DefeatRoaches --agent pysc2.agents.scripted_agent.DefeatRoaches
```

Run the Nidup Scripted Agents
-----------------------------

These agents have been built to work properly on the Simple64 map, as a Terran, and are not robust enough to play elsewhere.

Infinite Scouting Agent:
```
$ python3.6 -m pysc2.bin.agent --map Simple64 --agent nidup.pysc2.scripted_agents.ScoutingAgent --agent_race T
```

Build Order Agent:
```
$ python3.6 -m pysc2.bin.agent --map Simple64 --agent nidup.pysc2.scripted_agents.BuildOrderAgent --agent_race T
```

Run the Nidup Reinforcement Learning Agent
------------------------------------------

It's [based on these tutorials](https://itnext.io/build-a-sparse-reward-pysc2-agent-a44e94ba5255)

Train the Smart Agent by playing a lot of games:
```
$ python3.6 -m pysc2.bin.agent --map Simple64 --agent nidup.pysc2.smart_agents.ReinforcementAgent --agent_race T --norender --max_agent_steps=100000
```

The option `--norender` can be added to disable the rendering and play game faster.

The option `--max_agent_steps` can be added to make the agent play longer. The default value is 2500.

On my laptop, with no render,
 - 100k agent steps ~= 30 episodes ~= 30 minutes
 - 400k agent steps ~= 144 episodes ~= 100 minutes

Run the Smart Agent after the reinforcement:
```
$ python3.6 -m pysc2.bin.agent --map Simple64 --agent nidup.pysc2.smart_agents.ReinforcementAgent --agent_race T
```

Generate the learning report graph:
```
$ python3.6 generate_report.py --agent-name nidup.pysc2.smart_agents.ReinforcementAgent
```

Data & Analysis
---------------

**Game Results**

The game results are stored in `data` folder using a different file per agent.
The file is suffixed by `_results` and contains a pandas DataFrame.

**QLearning Table**

The reward history and final QLearning Table are stored in `data` folder using a different file per agent.
The file is suffixed by `_qlearning` and contains a pandas DataFrame.
This archive is re-used when it exists, you can drop it to train the agent from scratch.

Credits
-------

Thank you @skjb for the following [tutorial](https://github.com/skjb/pysc2-tutorial) 🚀
