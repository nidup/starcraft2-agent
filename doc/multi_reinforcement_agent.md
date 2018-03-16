Multi Reinforcement Agent (Machine Learning)
============================================

This agent uses the same Q-Learning approach than the [Reinforcement Attack Agent](reinforcement_attack_agent.md).

However, it has several learning models, each being specialized into a different phase.

```
$ python3.6 -m pysc2.bin.agent --map Simple64 --agent nidup.pysc2.agents.MultiReinforcementAgent --agent_race T --max_agent_steps=3000000  --difficulty 3
```

