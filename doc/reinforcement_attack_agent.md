Hybrid Reinforcement Attack Agent (Machine Learning)
====================================================

This agent uses the same Q-Learning approach than the [Reinforcement Marine Agent](reinforcement_marine_agent.md).

However, the learning is specialized on the train units & attack phase.

On the other hand, the build order phase is scripted to reduce the set of actions and focus the training on the attack.

```
$ python3.6 -m pysc2.bin.agent --map Simple64 --agent nidup.pysc2.agents.HybridAttackReinforcementAgent --agent_race T --max_agent_steps=1000000
```

Variants & Evolution
--------------------

Playing against the default built-in AI (very-easy difficulty).

Build order with 2 supply depots & 2 barracks (same than previous agent):

![Image of HybridAttackReinforcementAgent 1](HybridAttackReinforcementAgent_2_supply_2_rax.png)

Build order with 4 supply depots & 2 barracks to avoid supply limit and loss in mid-game:

![Image of HybridAttackReinforcementAgent 2](HybridAttackReinforcementAgent_4_supply_2_rax.png)

Build order with 10 supply depots & 4 barracks, ie, the marines ball:

![Image of HybridAttackReinforcementAgent 3](HybridAttackReinforcementAgent_10_supply_4_rax.png)

