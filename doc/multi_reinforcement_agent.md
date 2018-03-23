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

We observe here the agent struggles to learn, as it looses way too much games, it seems does not learn good enough pattern.

Watching replays we see it attacks by very small waves of units that are progressively detroyed.

Then it looses the episode due to a enemy's push or economically because enemy builds a B2 and sometimes B3.

![Image of MultiReinforcementAgent 4](MultiReinforcementAgent/4_qlearning_brains.png)

```
Results on the 100 last games:
race	total	win	draw	loss	win %	draw %	loss %
zerg	32	4	2	26	12.5	6.25	81.25
terran	30	1	4	25	3.33	13.33	83.33
protoss	38	3	1	34	7.89	2.63	89.47
```

Variant & Evolution (Time Matters)
----------------------------------

One major issue we observe it to try to learn from a not finished action or set of actions (aka order).

For instance, when attacking a game quadrant, the army has to go there before to do any damage and the reward should be applied only once the order really done, not when the army is still moving to the destination.

It shows a major flaw in the current system, the notion of is an order is really finished? how to detect an order has been taken in account? how to detect the order is finished?

It leads to introduce a time notion which makes everything more complex.

For this notion we can use episode steps, more information can be [found here](https://github.com/deepmind/pysc2/blob/master/docs/environment.md#game-and-action-speed).

Another though is that we should be able to learn on more high level items than orders.

Each order is a set of atomic player's action (select barracks + train marine) and can be seen as tactics items.

We introduces the concept of goals, a set of ordered orders, like:
 - BuildOrder
 - ReinforceArmy
 - AttackQuadrant

It allows to train the agent on the result of these goals on not on each atomic order or even worse atomic action.

As POC, to validate the concept, we replace the BuildOrder & Training Commanders by a simple GoalCommander, keeping Scout, Worker and Attack Commanders

The results are pretty good even if they results into lot of draw episodes.

Watching replays, we see the benefits of training on larger set of actions.

![Image of MultiReinforcementAgent 5](MultiReinforcementAgent/introduce_goals.png)

```
Results on the 100 last games:
race	total	win	draw	loss	win %	draw %	loss %
zerg	35	22	9	4	62.86	25.71	11.43
terran	32	13	12	7	40.62	37.5	21.88
protoss	33	11	16	6	33.33	48.48	18.18
```
