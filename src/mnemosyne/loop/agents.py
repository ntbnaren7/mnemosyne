from datetime import datetime
from typing import Dict, Any, List
from ..core.schemas import (
    ReasoningLoop, ReasoningStep, LoopStage, Post, Creative, 
    Insight, InsightContradiction, IntentType, AuthorType, StrategyChange, RiskLevel,
    LinkStrength
)
from ..core.interfaces import ReasoningAgent
from ..core.semantic import SemanticEngine

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
    async def process(self, loop: ReasoningLoop, context: Dict[str, Any]) -> ReasoningStep:
        intent = "Generate content drafts based on the active plan."
        hypothesis = "Visualizing the 'Reasoning Loop' will trigger more clarify-seeking comments."
        rationale = "The previous step decided to focus on simplicity. A diagram is the simplest way to explain the loop."
        
        # In V0, we mock the content generation
        post = Post(
            id="post_001",
            narrative_id=context.get("narrative").id,
            content_text="Mnemosyne is the brain of Simbli. It thinks before it speaks.",
            platform="Twitter",
            creatives=[Creative(id="img_001", type="image", attributes={"subject": "abstract brain network", "style": "minimalist"})]
        )
        
        decisions = [f"Created draft post: {post.id}", "Requested minimalist creative asset"]
        context["post"] = post
        context_used = [context.get("narrative").id]
        
        return self.create_step(
            stage=LoopStage.GENERATE, 
            intent=intent, 
            rationale=rationale, 
            decisions=decisions, 
            context_used=context_used, 
            hypothesis=hypothesis
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
    def __init__(self):
        self.semantic = SemanticEngine()

    async def process(self, loop: ReasoningLoop, context: Dict[str, Any]) -> ReasoningStep:
        intent = "Analyze signals and evaluate hypothesis."
        comments = context.get("comments", [])
        assumptions = context.get("assumptions", [])
        
        # Heuristic Contradiction Detection -> Semantic V1
        critiques = [c for c in comments if c.intent == IntentType.CRITIQUE]
        
        decisions = []
        contradictions = []
        
        # V1 Semantic Logic: Check for semantic clashes with Assumptions
        for assumption in assumptions:
            # Generate embedding for assumption if missing (lazy load for demo)
            if not assumption.embedding:
                assumption.embedding = self.semantic.encode(assumption.statement)
            
            for critique in critiques:
                if not critique.embedding or not assumption.embedding:
                    continue

                # Compute Similarity
                score = self.semantic.similarity(assumption.embedding, critique.embedding)
                
                # Determine Link Strength based on semantic score
                link_strength = None
                if score > 0.6:
                    link_strength = LinkStrength.STRONG
                elif score > 0.4:
                    link_strength = LinkStrength.MODERATE
                elif score > 0.25:
                    link_strength = LinkStrength.WEAK
                
                if link_strength:
                    # Calculate weighted delta
                    delta_map = {
                        LinkStrength.STRONG: 0.15,
                        LinkStrength.MODERATE: 0.08,
                        LinkStrength.WEAK: 0.02
                    }
                    confidence_delta = delta_map[link_strength]

                    contradiction = InsightContradiction(
                        insight_id=assumption.id, # We allow assumptions here as per schema update logic
                        source_id=critique.id,
                        rationale=f"Semantic contradiction detected (Score: {score:.2f}) with: '{critique.content[:50]}...'",
                        confidence_delta=confidence_delta,
                        link_strength=link_strength,
                        semantic_score=score
                    )
                    contradictions.append(contradiction)
                    decisions.append(f"DETECTED SEMANTIC CONTRADICTION ({link_strength.value.upper()}) for {assumption.id} (Score: {score:.2f})")
                    
                    # Store pivot data for first Strong hit (for StrategyChange demo flow)
                    if link_strength == LinkStrength.STRONG and "pivot_data" not in context:
                        context["pivot_data"] = {
                            "insight_id": assumption.id, # Using assumption ID as the key for now
                            "previous_assumption": assumption.statement,
                            "confidence_from": assumption.current_confidence,
                            "confidence_to": max(0.0, assumption.current_confidence - confidence_delta),
                            "triggering_signals": [critique.content]
                        }

        
        if not contradictions:
            decisions.append("No active contradictions detected in high-signal comments.")
        
        context["contradictions"] = contradictions
        rationale = f"Analyzed {len(comments)} comments. Found {len(critiques)} critique(s) with {len(contradictions)} semantic links."
        
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
