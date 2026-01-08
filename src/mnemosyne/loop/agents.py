from datetime import datetime
from typing import Dict, Any, List
import uuid
from ..core.schemas import (
    ReasoningLoop, ReasoningStep, LoopStage, Post, Creative, 
    Insight, InsightContradiction, IntentType, AuthorType, StrategyChange, RiskLevel,
    VisualIntent, ImageArtifact
)
from ..core.interfaces import ReasoningAgent
from .renderer import MockStableDiffusionRenderer

class BaseMockAgent:
    """Helper for mock agents to create steps with rationale."""
    def create_step(self, stage: LoopStage, intent: str, rationale: str, decisions: List[str], context_used: List[str] = [], referenced_insights: List[str] = [], referenced_assumptions: List[str] = [], memory_override_reason: str = None, strategy_change_id: str = None, hypothesis: str = None) -> ReasoningStep:
        return ReasoningStep(
            stage=stage,
            intent=intent,
            rationale=rationale,
            decisions=decisions,
            context_used=context_used,
            referenced_insights=referenced_insights,
            referenced_assumptions=referenced_assumptions,
            memory_override_reason=memory_override_reason,
            strategy_change_id=strategy_change_id,
            hypothesis=hypothesis,
            human_approved=False # V0 default
        )

class PlanAgent(BaseMockAgent, ReasoningAgent):
    async def process(self, loop: ReasoningLoop, context: Dict[str, Any]) -> ReasoningStep:
        org = context.get("organization")
        narrative = context.get("narrative")
        insights = context.get("insights", [])
        assumptions = context.get("assumptions", [])
        
        # MANDATORY MEMORY & ASSUMPTION BINDING
        referenced_insights = [i.id for i in insights if i.confidence > 0.5]
        referenced_assumptions = [a.id for a in assumptions if a.current_confidence > 0.0]
        
        memory_override_reason = context.get("memory_override_reason")
        
        # V0 Primitive Final Rule: No Plan without Assumption
        if not referenced_assumptions and not memory_override_reason:
            raise ValueError(
                "CRITICAL: Planning failed. Every PLAN step MUST reference at least one active Assumption "
                "OR explicitly record a justification for ignoring existing memory."
            )
            
        intent = f"Develop a content plan for narrative: {narrative.title}"
        hypothesis = "Employee-led storytelling will maintain narrative continuity."
        rationale = f"Based on {org.name}'s current insights, we are double-downing on what works."
        decisions = ["Assign employee-led content piece", "Target existing technical audience"]
        
        # Risk Validation
        for a_id in referenced_assumptions:
            assumption = next((a for a in assumptions if a.id == a_id), None)
            if assumption and assumption.risk_level == RiskLevel.HIGH:
                decisions.append(f"WARNING: Proceeding with High Risk Assumption {a_id}. Validation required.")
        
        return self.create_step(
            stage=LoopStage.PLAN, 
            intent=intent, 
            rationale=rationale, 
            decisions=decisions, 
            context_used=[org.id, narrative.id],
            referenced_insights=referenced_insights,
            referenced_assumptions=referenced_assumptions,
            memory_override_reason=memory_override_reason,
            hypothesis=hypothesis
        )

class GenerateAgent(BaseMockAgent, ReasoningAgent):
    def __init__(self):
        self.renderer = MockStableDiffusionRenderer()

    async def process(self, loop: ReasoningLoop, context: Dict[str, Any]) -> ReasoningStep:
        intent = "Create assets aligned with the plan."
        
        # Determine Visual Intent from Context
        # For V0.5 Test, we assume the Plan or Context specifies the Visual Intent
        requested_visual_intent = context.get("requested_visual_intent")
        
        decisions = []
        
        if requested_visual_intent:
            visual_intent = requested_visual_intent
            image_artifact = await self.renderer.render(visual_intent)
            
            # Create Creative Asset
            creative = Creative(
                id=f"crt_{uuid.uuid4().hex[:8]}",
                post_id="pending",
                asset_type="image",
                content="Visual asset based on strategic intent",
                visual_intent=visual_intent,
                image_artifact=image_artifact,
                status="generated"
            )
            # Store in context for Publish/Observe stages to reference
            context["generated_creative"] = creative
            
            decisions.append(f"Generated Image {image_artifact.artifact_id} with Intent: {visual_intent.to_prompt_string()}")
            decisions.append(f"Created Creative {creative.id}")
        else:
            decisions.append("Created draft post: post_001")
            decisions.append("Requested minimalist creative asset (Text Only)")
            
        return self.create_step(
            stage=LoopStage.GENERATE, 
            intent=intent, 
            rationale="Executed visual production using Stable Diffusion Renderer.", 
            decisions=decisions
        )

class PublishAgent(BaseMockAgent, ReasoningAgent):
    async def process(self, loop: ReasoningLoop, context: Dict[str, Any]) -> ReasoningStep:
        intent = "Obtain human approval for publishing."
        rationale = "V0 Mandate: All publishing requires human-in-the-loop."
        
        # This would normally wait for an external signal
        # For mock, we assume it's pending
        decisions = ["Awaiting human sign-off on Post post_001"]
        
        step = self.create_step(
            stage=LoopStage.PUBLISH, 
            intent=intent, 
            rationale=rationale, 
            decisions=decisions
        )
        # In a real app, human_approved would be set by a controller/UI
        return step

from .ingestion import CommentIngestor

class ObserveAgent(BaseMockAgent, ReasoningAgent):
    async def process(self, loop: ReasoningLoop, context: Dict[str, Any]) -> ReasoningStep:
        intent = "Collect signals from the published post."
        rationale = "Ingesting raw comment data to extract high-signal feedback."
        
        ingestor = CommentIngestor()
        # In a real scenario, this path would be dynamic or provided via context
        comments = ingestor.ingest_from_file("raw_comments.json", post_id="post_001")
        
        decisions = [f"Ingested {len(comments)} comments from platform export"]
        context["comments"] = comments
        
        return self.create_step(
            stage=LoopStage.OBSERVE, 
            intent=intent, 
            rationale=rationale, 
            decisions=decisions
        )

class InterpretAgent(BaseMockAgent, ReasoningAgent):
    async def process(self, loop: ReasoningLoop, context: Dict[str, Any]) -> ReasoningStep:
        intent = "Analyze signals and evaluate hypothesis."
        comments = context.get("comments", [])
        insights = context.get("insights", [])
        
        # Heuristic Contradiction Detection
        critiques = [c for c in comments if c.intent == IntentType.CRITIQUE]
        skepticism_count = len(critiques)
        
        decisions = []
        contradictions = []
        
        # V0.5 Causal Analysis: Did visual attributes affect intent?
        generated_creative = context.get("generated_creative")
        if generated_creative and generated_creative.visual_intent:
            v_intent = generated_creative.visual_intent
            
            # Hypothesis: "Human presence increases identity-seeking questions"
            identity_questions = [c for c in comments if "contact" in c.content.lower() or "who" in c.content.lower()]
            
            if v_intent.human_presence == "explicit" and len(identity_questions) > 0:
                 decisions.append(f"CAUSAL LINK FOUND: Explicit human presence -> {len(identity_questions)} identity signals.")
                 # Strengthen assumption if it exists
            elif v_intent.human_presence == "none" and len(identity_questions) == 0:
                 decisions.append("CAUSAL LINK FOUND: No human presence -> Zero identity signals.")
            
        
        # Scenario-specific contradiction check for Demo
        # Insight: "Employee-led content increases genuine questions"
        for insight in insights:
            if "Employee-led" in insight.content and skepticism_count > 1:
                confidence_from = insight.confidence
                delta = 0.3
                confidence_to = max(0.0, confidence_from - delta)
                
                contradiction = InsightContradiction(
                    insight_id=insight.id,
                    source_id=loop.id,
                    rationale=f"Observed {skepticism_count} critiques/skepticism signals, contradicting expected question-led engagement.",
                    confidence_delta=delta
                )
                contradictions.append(contradiction)
                decisions.append(f"DETECTED CONTRADICTION for Insight {insight.id} ({confidence_from:.2f} -> {confidence_to:.2f})")
                
                # Pass data for Adapt
                context["pivot_data"] = {
                    "insight_id": insight.id,
                    "previous_assumption": insight.content,
                    "confidence_from": confidence_from,
                    "confidence_to": confidence_to,
                    "triggering_signals": [c.content for c in critiques]
                }
        
        if not contradictions:
            decisions.append("No active contradictions detected in high-signal comments.")
        
        context["contradictions"] = contradictions
        rationale = f"Analyzed {len(comments)} comments. Found {skepticism_count} critique(s)."
        
        return self.create_step(
            stage=LoopStage.INTERPRET, 
            intent=intent, 
            rationale=rationale, 
            decisions=decisions
        )

class AdaptAgent(BaseMockAgent, ReasoningAgent):
    async def process(self, loop: ReasoningLoop, context: Dict[str, Any]) -> ReasoningStep:
        intent = "Refine strategy based on interpretations and emit rationale."
        contradictions = context.get("contradictions", [])
        pivot_data = context.get("pivot_data")
        assumptions = context.get("assumptions", [])
        
        strategy_change = None
        
        if contradictions and pivot_data:
            # Detect which assumptions are affected (heuristic for demo)
            affected_assumption = next((a for a in assumptions if "employee" in a.statement.lower()), None)
            related_assumption_ids = [affected_assumption.id] if affected_assumption else []
            
            # Emit StrategyChange as required
            strategy_change = StrategyChange(
                insight_id=pivot_data["insight_id"],
                related_assumption_ids=related_assumption_ids,
                previous_assumption=pivot_data["previous_assumption"],
                triggering_signals=pivot_data["triggering_signals"],
                confidence_from=pivot_data["confidence_from"],
                confidence_to=pivot_data["confidence_to"],
                decision="Shift content focus from internal engineering narratives to technical transparency documentation.",
                justification=(
                    "We observed significant fatigue and skepticism from our audience regarding 'corporate/employee' narratives. "
                    "The signals suggest that purely internal engineer voices are being perceived as 'marketing fluff'. "
                    "To maintain trust, we must pivot to more objective, documentation-style technical content."
                ),
                acknowledged_risks=[
                    "This move might decrease initial engagement volume (virality).",
                    "Engineering team might feel less directly involved in the narrative."
                ],
                review_horizon=datetime(2026, 2, 8) # One month review
            )
            
            # Update Assumption Confidence based on Strategy Change
            if affected_assumption:
                affected_assumption.current_confidence = pivot_data["confidence_to"]
                affected_assumption.invalidation_signals.extend(pivot_data["triggering_signals"])
                # Logic to update risk level is in MemoryManager.apply_decay or can be explicit here, 
                # but for V0 persistence, we assume memory manager handles state updates or we update the object reference held by memory.
            
            context["strategy_change"] = strategy_change
            rationale = "Strategic revision triggered by signal contradiction."
            decisions = [
                f"Emit StrategyChange {strategy_change.id}", 
                f"Weakened Assumption {affected_assumption.id if affected_assumption else 'N/A'}",
                "Update future narrative templates"
            ]
        else:
            # If we are here and expected a change, we should fail, but for the demo, 
            # we'll just handle the absence as a failure if it was mandatory.
            if not contradictions:
                 # If no contradiction, we might not need to ADAPT, 
                 # but if the loop continues to ADAPT, we must explain why we aren't changing.
                 strategy_change = StrategyChange(
                     previous_assumption="Existing strategy is robust.",
                     triggering_signals=["No significant critiques found."],
                     confidence_from=1.0,
                     confidence_to=1.0,
                     decision="Maintain current strategy.",
                     justification="Performance signals align with current beliefs.",
                     acknowledged_risks=["Potential to miss emerging negative signals due to low volume."],
                     review_horizon=datetime(2026, 1, 22)
                 )
                 context["strategy_change"] = strategy_change
                 rationale = "Maintaining current strategic course."
                 decisions = ["No changes required."]

        if not strategy_change:
            raise ValueError("CRITICAL: Adapt phase completed without emitting a StrategyChange object.")
            
        return self.create_step(
            stage=LoopStage.ADAPT, 
            intent=intent, 
            rationale=rationale, 
            decisions=decisions,
            strategy_change_id=strategy_change.id
        )
