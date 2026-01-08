from typing import Protocol, runtime_checkable, Any, Dict
from .schemas import ReasoningLoop, ReasoningStep, LoopStage

@runtime_checkable
class ReasoningAgent(Protocol):
    """Interface for a modular reasoning component."""
    
    async def process(self, loop: ReasoningLoop, context: Dict[str, Any]) -> ReasoningStep:
        """
        Execute a step in the reasoning loop.
        
        Args:
            loop: The current state of the reasoning loop.
            context: Additional external context (org data, previous results).
            
        Returns:
            A ReasoningStep containing decisions and rationale.
        """
        ...

class LoopOrchestrator:
    """Manages the transition between stages of the reasoning loop."""
    
    def __init__(self):
        self.stages: Dict[LoopStage, ReasoningAgent] = {}

    def register_agent(self, stage: LoopStage, agent: ReasoningAgent):
        self.stages[stage] = agent

    async def run_next(self, loop: ReasoningLoop, context: Dict[str, Any]) -> ReasoningLoop:
        if loop.current_stage not in self.stages:
            raise ValueError(f"No agent registered for stage: {loop.current_stage}")
            
        agent = self.stages[loop.current_stage]
        step = await agent.process(loop, context)
        
        loop.steps.append(step)
        loop.current_stage = self._get_next_stage(loop.current_stage)
        return loop

    def _get_next_stage(self, current: LoopStage) -> LoopStage:
        stages = list(LoopStage)
        current_index = stages.index(current)
        next_index = (current_index + 1) % len(stages)
        return stages[next_index]
