Starcraft2 Nidup's agents
=========================

Discovering PySC2 - StarCraft II Learning Environment, playing with reinforcement learning 🤖

Can be installed following [this doc](doc/install.md)

Notes
-----

These agents have been built to work properly on the Simple64 map, as a Terran player.
They are not robust enough to play elsewhere.

Basic agents (scripted)
-----------------------

Here are [few scripted agents](doc/scripted_agents.md) (built to discover the API).

Reinforcement Marine Agent (Machine Learning)
---------------------------------------------

This agent uses a QLearning table on a reduced set of actions, build supply depot, barrack, train marine & attack.

It has been slightly fine-tuned to be trained faster and win more games against the built-in AI.

![Image of ReinforcementMarineAgent 4](doc/ReinforcementMarineAgent_enemyb1andb2.png)

Hybrid Reinforcement Attack Agent (Machine Learning)
----------------------------------------------------

This agent uses the same QLearning approach but specialized on the train units & attack phase.

The build order phase is scripted to reduce the set of actions and focus the training on the attack.

```
$ python3.6 -m pysc2.bin.agent --map Simple64 --agent nidup.pysc2.agents.HybridAttackReinforcementAgent --agent_race T --max_agent_steps=1000000
```

Data & Analysis
---------------

The game results are stored in `data` folder using a different file per agent.

The file is suffixed by `_results` and contains a pandas DataFrame.

Generate the result report graph:
```
$ python3.6 generate_report.py --agent-name nidup.pysc2.agents.ReinforcementMarineAgent
```

Query the game results:
```
$ python3.6 generate_report.py --agent-name nidup.pysc2.agents.ReinforcementMarineAgent --filter win
```

Credits
-------

Thank you @skjb for the following [tutorial](https://github.com/skjb/pysc2-tutorial) 🚀
