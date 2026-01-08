import asyncio
import json
import uuid
import os
from datetime import datetime
from mnemosyne.core.schemas import (
    Organization, Narrative, ReasoningLoop, LoopStage, Insight, 
    Assumption, RiskLevel, VisualIntent
)
from mnemosyne.core.interfaces import LoopOrchestrator
from mnemosyne.loop.agents import (
    PlanAgent, GenerateAgent, PublishAgent, 
    ObserveAgent, InterpretAgent, AdaptAgent
)
from mnemosyne.memory.manager import MemoryManager

# --- MOCK DATA ---
CONTROL_COMMENT_DATA = [
    {"comment_id": "c1", "post_id": "post_001", "author": "UserA", "text": "Nice generic graphic.", "timestamp": "2025-01-01T12:00:00Z"},
    {"comment_id": "c2", "post_id": "post_001", "author": "UserB", "text": "Clean design.", "timestamp": "2025-01-01T12:05:00Z"},
    {"comment_id": "c3", "post_id": "post_001", "author": "UserC", "text": "Good update.", "timestamp": "2025-01-01T12:10:00Z"}
]

VARIANT_COMMENT_DATA = [
    {"comment_id": "v1", "post_id": "post_001", "author": "UserD", "text": "Who is this engineer? They look familiar.", "timestamp": "2025-01-02T12:00:00Z"},
    {"comment_id": "v2", "post_id": "post_001", "author": "UserE", "text": "Can I contact this person directly?", "timestamp": "2025-01-02T12:05:00Z"},
    {"comment_id": "v3", "post_id": "post_001", "author": "UserF", "text": "Is this a real employee or stock photo?", "timestamp": "2025-01-02T12:10:00Z"}
]

def write_mock_comments(comments):
    with open("raw_comments.json", "w") as f:
        json.dump(comments, f, indent=2)

async def run_visual_experiment():
    print("--- MNEMOSYNE V0.5: VISUAL SIGNAL VALIDATION ---")
    
    memory = MemoryManager(storage_dir="storage_visual_test")
    # Setup basics
    org = Organization(id="simbli_test", name="Simbli", mission="Test", core_values=[], target_audience=[], strategic_priorities=[])
    narrative = Narrative(id="narr_test", org_id=org.id, title="Visual Causality", objectives=[], key_messages=[])
    memory.add_organization(org)
    memory.add_narrative(narrative) # Fixed: Add narrative to memory
    
    # Orchestrator
    orchestrator = LoopOrchestrator()
    orchestrator.register_agent(LoopStage.PLAN, PlanAgent())
    orchestrator.register_agent(LoopStage.GENERATE, GenerateAgent())
    orchestrator.register_agent(LoopStage.PUBLISH, PublishAgent())
    orchestrator.register_agent(LoopStage.OBSERVE, ObserveAgent())
    orchestrator.register_agent(LoopStage.INTERPRET, InterpretAgent())
    orchestrator.register_agent(LoopStage.ADAPT, AdaptAgent())

    # --- CONTROL RUN ---
    print("\n[EXPERIMENT 1: CONTROL] (No Human Presence)")
    write_mock_comments(CONTROL_COMMENT_DATA)
    
    control_intent = VisualIntent(
        human_presence="none",
        face_count="0",
        visual_style="abstract",
        composition="text_led"
    )
    
    loop_control = ReasoningLoop(id="loop_control", org_id=org.id)
    context_control = {
        "organization": org,
        "narrative": narrative,
        "insights": [],
        "assumptions": [], # Mock empty assumptions to avoid PlanAgent Check failure - Wait, PlanAgent requires assumption!
        "requested_visual_intent": control_intent
    }
    
    # We need a dummy assumption for PlanAgent to be happy
    dummy_asm = Assumption(id="asm_dummy", statement="Visuals allow testing.", supporting_insights=[], current_confidence=1.0)
    context_control["assumptions"] = [dummy_asm]
    
    # Run loop
    for _ in range(6):
        loop_control = await orchestrator.run_next(loop_control, context_control)
        print(f"  {loop_control.current_stage}: {loop_control.steps[-1].decisions}")

    # --- VARIANT RUN ---
    print("\n[EXPERIMENT 2: VARIANT] (Explicit Human Presence)")
    write_mock_comments(VARIANT_COMMENT_DATA)
    
    variant_intent = VisualIntent(
        human_presence="explicit",
        face_count="1-2",
        visual_style="illustrative",
        composition="subject_centered"
    )
    
    loop_variant = ReasoningLoop(id="loop_variant", org_id=org.id)
    context_variant = {
        "organization": org,
        "narrative": narrative,
        "insights": [],
        "assumptions": [dummy_asm],
        "requested_visual_intent": variant_intent
    }
    
    # Run loop
    for _ in range(6):
        loop_variant = await orchestrator.run_next(loop_variant, context_variant)
        print(f"  {loop_variant.current_stage}: {loop_variant.steps[-1].decisions}")
             
    print("\n--- CONCLUSION ---")
    print("Verifying if visual attributes caused different reasoning outcomes...")
    # Just need to check logs for now

if __name__ == "__main__":
    asyncio.run(run_visual_experiment())
