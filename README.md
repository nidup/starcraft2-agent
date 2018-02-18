Starcraft 2 agent
=================

Discovering PySC2 - StarCraft II Learning Environment, playing with simple agent 🤖

Install 
-------

Install [PySC2 - StarCraft II Learning Environment](https://github.com/deepmind/pysc2)

```
$ pip install pysc2
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
python -m pysc2.bin.play --map Simple64
```

More options and details can be found on [PySC2 - StarCraft II Learning Environment](https://github.com/deepmind/pysc2)


**Troubleshooting**

```
File "/usr/lib/python2.7/dist-packages/pygame/_numpysurfarray.py", line 437, in blit_array surface.get_buffer ().write (data, 0) IndexError: bytes to write exceed buffer size
```

Solved by upgrading pygame from 1.9.1 to  1.9.3:

```
pip install pygame --upgrade
```

Run the agent
-------------

```
$ cd ~/git/starcraft2-agent/src/
$ python -m pysc2.bin.agent --map Simple64 --agent simple_agent.SimpleAgent --agent_race T
```

Credits
-------

Thank you @skjb for the following [tutorial](https://github.com/skjb/pysc2-tutorial) 🚀
