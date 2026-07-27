# Session 07: Conditional Routing (V3.4)

## What We Built
- Configured dynamic execution paths using LangGraph's `add_conditional_edges`.
- Built `workflow/router.py` containing `route_after_classifier`.
- Implemented logic that inspects the shared `CreativeState` to determine whether to pass the graph to `commercial_agent_node` or `story_agent_node`.
- Set up `rich` to enable professional, color-coded python stack traces for significantly easier debugging.

## Milestone Review (Mentor Mode)
1. **What was done well:** Understanding the logic of isolating routing logic outside of the nodes themselves. 
2. **Biggest weakness:** Forgetting to add initialized nodes to the graph builder (`builder.add_node`). If a node isn't registered, it cannot be routed to!
3. **One production concern missed:** What happens if the classifier returns an unknown string that isn't handled in the router? Currently we fallback to `END`, but in a strict production environment, we might want to route to a `human_intervention` node.
4. **One thing to improve next:** Transitioning the router to handle Human-in-the-Loop interruptions if missing information is detected.

## Next Steps for Session 08
- **V3.5 - Tool Calling:** Equip agents with tools (like reading a brand's website or PDF) so they can gather facts autonomously instead of just relying on their pre-trained weights.
