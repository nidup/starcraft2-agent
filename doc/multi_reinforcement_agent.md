Multi Reinforcement Agent (Machine Learning)
============================================

This agent uses the same Q-Learning approach than the [Reinforcement Attack Agent](reinforcement_attack_agent.md).

However, it has several learning models, each being specialized into a different phase.

```
$ python3.6 -m pysc2.bin.agent --map Simple64 --agent nidup.pysc2.agents.MultiReinforcementAgent --agent_race T --max_agent_steps=3000000  --difficulty 3
```

Variants & Evolution (Sequential Build Order + Assisted Timing Push + Attack Training per Race)
-----------------------------------------------------------------------------------------------

**Against [medium built-in AI](https://github.com/deepmind/pysc2/blob/master/pysc2/env/sc2_env.py#L51)**

![Image of MultiReinforcementAgent 1](MultiReinforcementAgent/sequential.png)

```
Results on the 100 last games:
race	total	win	draw	loss	win %	draw %	loss %
zerg	32	12	4	16	37.5	12.5	50.0
terran	32	5	0	27	15.62	0	84.38
protoss	30	1	0	29	3.33	0	96.67
```
