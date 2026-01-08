from typing import Protocol, runtime_checkable, Any, Dict
from .schemas import (
    ReasoningLoop, ReasoningStep, LoopStage, Insight, Organization, Narrative,
    VisualIntent, ImageArtifact
)

@runtime_checkable
class ReasoningAgent(Protocol):
    """Protocol for any agent in the reasoning loop."""
    async def process(self, loop: ReasoningLoop, context: Dict[str, Any]) -> ReasoningStep:
        """
        Execute a step in the reasoning loop.
        
        Returns:
            A ReasoningStep containing decisions and rationale.
        """
        ...

@runtime_checkable
class ImageRenderer(Protocol):
    """Protocol for converting visual intent into an artifact."""
    async def render(self, intent: VisualIntent) -> ImageArtifact:
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
