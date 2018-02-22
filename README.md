Starcraft 2 agent
=================

Discovering PySC2 - StarCraft II Learning Environment, playing with simple agent 🤖

Install with Python 3.6
-----------------------

Install [PySC2 - StarCraft II Learning Environment](https://github.com/deepmind/pysc2)

```
$ python3.6 -m pip install setuptools
$ python3.6 -m pip install pysc2
$ sudo python3.6 -m pip install scipy
$ sudo python3.6 -m pip install sklearn
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

Run the agent
-------------

```
$ cd ~/git
$ git clone git@github.com:nidup/starcraft2-agent.git
$ cd ~/git/starcraft2-agent/
$ python3.6 -m pysc2.bin.agent --map Simple64 --agent nidup.pysc2.simple_agent.SimpleAgent --agent_race T
```

Credits
-------

Thank you @skjb for the following [tutorial](https://github.com/skjb/pysc2-tutorial) 🚀
