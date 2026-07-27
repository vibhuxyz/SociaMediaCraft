from typing import Callable, Dict, Optional, Any

class AgentRegistry:
    def __init__(self):
        self._agents: Dict[str, Callable] = {}
        self._conditions: Dict[str, Callable[[dict], bool]] = {}
        
    def register(self, name: str, runs_when: Optional[Callable[[dict], bool]] = None):
        def decorator(func: Callable):
            import functools
            
            # Prevent double-registration from overriding runs_when logic if imported twice
            if name in self._agents and runs_when is None and self._conditions.get(name) is not None:
                return self._agents[name]
                
            @functools.wraps(func)
            async def wrapper(state):
                # Evaluate explicit runs_when condition
                condition = self._conditions.get(name)
                if condition and not condition(state):
                    print(f"⏩ [Adaptive Orchestrator] Skipping {name} (capability/workflow condition not met)")
                    return {}
                        
                return await func(state)
            self._agents[name] = wrapper
            self._conditions[name] = runs_when
            return wrapper
        return decorator
        
    def get_all_agents(self) -> Dict[str, Callable]:
        return self._agents
        
    def get_agent(self, name: str) -> Callable:
        return self._agents[name]

# Global singleton registry
agent_registry = AgentRegistry()
