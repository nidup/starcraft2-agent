Multi Reinforcement Agent (Machine Learning)
============================================

This agent uses the same Q-Learning approach than the [Reinforcement Attack Agent](reinforcement_attack_agent.md).

However, it has several learning models, each being specialized into a different phase.

```
$ python3.6 -m pysc2.bin.agent --map Simple64 --agent nidup.pysc2.agents.MultiReinforcementAgent --agent_race T --max_agent_steps=3000000  --difficulty 3
```

**All the following results are collected playing against [medium built-in AI](https://github.com/deepmind/pysc2/blob/master/pysc2/env/sc2_env.py#L51)**

Variants & Evolution (Sequential Build Order + Assisted Timing Push + Attack Training per Race)
-----------------------------------------------------------------------------------------------

Also known as "3-Rax-rush-TvX-All-In -With-Former-Push" build orders.

![Image of MultiReinforcementAgent 1](MultiReinforcementAgent/sequential.png)

```
Results on the 100 last games:
race	total	win	draw	loss	win %	draw %	loss %
zerg	32	12	4	16	37.5	12.5	50.0
terran	32	5	0	27	15.62	0	84.38
protoss	30	1	0	29	3.33	0	96.67
```

Variant & Evolution (QLearning to Choose a Build Order per Race)
----------------------------------------------------------------

We add the capability to scout the race very soon in the game, the BuildOrdersCommander is able to choose a build orders.

We re-enforce the choose of a build orders by rewarding on the episode victory.

We also introduce the capacity to build hellion & medivac.

This change makes the attack space bigger and it can slow down a lot the attack training or results into very disparate army compositions.

In the future, we could split the attack QLearning system to:
 - split training units actions & attack actions
 - reduce the training units state & actions by specializing by build orders

A new report allows to see the progress of the use of each build orders in time for each race.

```
Results on the 100 last games:
race	total	win	draw	loss	win %	draw %	loss %
zerg	38	10	1	27	26.32	2.63	71.05
terran	30	3	0	27	10.0	0	90.0
protoss	32	0	0	32	0	0	100.0
```

We can see interesting changes, from the selection of certain build orders for Zerg and Terran:

![Image of MultiReinforcementAgent 2](MultiReinforcementAgent/build_orders_selection_zerg.png)

And also a equivalent use of any build orders against Protoss (as the agent loose every episode against this race):

![Image of MultiReinforcementAgent 3](MultiReinforcementAgent/build_orders_selection_protoss.png)


Variant & Evolution (QLearning on Build Orders, Units Training, Attack Quadrants, Attack Base)
----------------------------------------------------------------------------------------------

We split here the QLearning as 4 dedicated "brains":
 - Build Orders (BO) choice depending on race, rewarded on the game results
 - Training of units depending on race and selected BO, rewarded on the game results
 - Attack of one of the four game quadrants rewarded on destroyed buildings
 - Attack in a game quadrant rewarded on destroyed buildings & unit

