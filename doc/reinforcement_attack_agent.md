Hybrid Reinforcement Attack Agent (Machine Learning)
====================================================

This agent uses the same Q-Learning approach than the [Reinforcement Marine Agent](reinforcement_marine_agent.md).

However, the learning is specialized on the train units & attack phase.

On the other hand, the build order phase is scripted to reduce the set of actions and focus the training on the attack.

```
$ python3.6 -m pysc2.bin.agent --map Simple64 --agent nidup.pysc2.agents.HybridAttackReinforcementAgent --agent_race T --max_agent_steps=1000000
```

Variants & Evolution (Marines only)
-----------------------------------

**Against [very-easy built-in AI](https://github.com/deepmind/pysc2/blob/master/pysc2/env/sc2_env.py#L51)**

Playing against the default built-in AI (very-easy difficulty).

Build order with 2 supply depots & 2 barracks (same than previous agent):

![Image of HybridAttackReinforcementAgent 1](HybridAttackReinforcementAgent_2_supply_2_rax.png)

Build order with 4 supply depots & 2 barracks to avoid supply limit and loss in mid-game:

![Image of HybridAttackReinforcementAgent 2](HybridAttackReinforcementAgent_4_supply_2_rax.png)

Build order with 10 supply depots & 4 barracks, ie, the marines ball:

![Image of HybridAttackReinforcementAgent 3](HybridAttackReinforcementAgent_10_supply_4_rax.png)

**Against [easy built-in AI](https://github.com/deepmind/pysc2/blob/master/pysc2/env/sc2_env.py#L51)**

```
python3.6 -m pysc2.bin.agent --map Simple64 --agent nidup.pysc2.agents.HybridAttackReinforcementAgent --agent_race T --max_agent_steps=1000000 --difficulty 2 -norender
```

Build order with 10 supply depots & 4 barracks, ie, the marines ball:

![Image of HybridAttackReinforcementAgent 4](HybridAttackReinforcementAgent_10_supply_4_rax-easy.png)

**Against [medium built-in AI](https://github.com/deepmind/pysc2/blob/master/pysc2/env/sc2_env.py#L51)**

```
python3.6 -m pysc2.bin.agent --map Simple64 --agent nidup.pysc2.agents.HybridAttackReinforcementAgent --agent_race T --max_agent_steps=1000000 --difficulty 3 -norender
```

Build order with 10 supply depots & 4 barracks, ie, the marines ball:

![Image of HybridAttackReinforcementAgent 5](HybridAttackReinforcementAgent_10_supply_4_rax-medium.png)


Variants & Evolution (Marines and Marauders)
--------------------------------------------

**Against [easy built-in AI](https://github.com/deepmind/pysc2/blob/master/pysc2/env/sc2_env.py#L51)**

Build order with 8 supply depots & 4 barracks & 2 refinery & 1 factory & 1 techlab barracks, ie, the MM ball:

The build order is sequential and has to be finished to let the train & attack phase starts.

![Image of HybridAttackReinforcementAgent 6](HybridAttackReinforcementAgent_8_supply_4_rax_2ref_1fac_1lab-easy.png)

The same build order, updated to make the build of the supply depots triggered only when needed:

![Image of HybridAttackReinforcementAgent 7](HybridAttackReinforcementAgent_8_supply_4_rax_2ref_1fac_1lab-2-easy.png)

**Against [medium built-in AI](https://github.com/deepmind/pysc2/blob/master/pysc2/env/sc2_env.py#L51)**

The same build order, updated to make the build of the supply depots triggered only when needed:

![Image of HybridAttackReinforcementAgent 8](HybridAttackReinforcementAgent_8_supply_4_rax_2ref_1fac_1lab-2-medium.png)


Variants & Evolution (Worker Commander)
---------------------------------------

**Against [easy built-in AI](https://github.com/deepmind/pysc2/blob/master/pysc2/env/sc2_env.py#L51)**

Build order with 8 supply depots & 4 barracks & 1 refinery & 1 factory & 1 techlab barracks, ie, the MM ball.

A worker commander has been added to:
  - fill each built refinery with 3 VCS
  - build as much VCS than VCS affected to gather vespene
  - be able to build extra VCS (4 has been added on this build)

At each step, the hybrid commander:
  - ask to the worker commander if it has an order
  - if not, it aks to the build order commander
  - if not, it asks to the the attack commander

The drawback is a slower start of the game due to blocking orders from the worker commander and the build order commander.

![Image of HybridAttackReinforcementAgent 9](HybridAttackReinforcementAgent_8_supply_4_rax_1ref_1fac_1lab-worker-easy.png)

Same build order but making the worker commander plays only every X game steps.

The worker commander gives orders to improve the production, it's less important than build order and attack commanders and can be called less often to accelerate the early game execution.

