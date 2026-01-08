import asyncio
import uuid
from datetime import datetime
from mnemosyne.core.schemas import (
    Organization, Narrative, ReasoningLoop, LoopStage, Insight, InsightContradiction,
    Assumption, RiskLevel, StrategyChange
)
from mnemosyne.core.interfaces import LoopOrchestrator
from mnemosyne.loop.agents import (
    PlanAgent, GenerateAgent, PublishAgent, 
    ObserveAgent, InterpretAgent, AdaptAgent
)
from mnemosyne.memory.manager import MemoryManager

async def run_mnemosyne_v0_final_demo():
    print("--- MNEMOSYNE V0: EXPLICIT ASSUMPTIONS DEMO ---")
    
    # 1. Setup Memory with a prior Insight and Assumption
    memory = MemoryManager(storage_dir="storage_v0_final")
    
    org = Organization(
        id="simbli_intl",
        name="Simbli",
        mission="Organize the world's strategic intelligence.",
        core_values=["Transparency", "Memory", "Precision"],
        target_audience=["AI Engineers", "Strategists"],
        strategic_priorities=["Launch Mnemosyne V0"]
    )
    memory.add_organization(org)
    
    narrative = Narrative(
        id="narrative_demo",
        org_id=org.id,
        title="Scaling Employee Voice",
        objectives=["Establish trust through internal transparency"],
        key_messages=["Our engineers are the source of truth"]
    )
    memory.add_narrative(narrative)
    
    # Prior Insight
    prior_insight = Insight(
        id="ins_001",
        content="Employee-led content increases genuine questions and high-signal engagement.",
        confidence=0.9,
        source_loop_ids=["loop_past_001"]
    )
    memory.add_insight(prior_insight)
    
    # NEW: Active Assumption
    assumption = Assumption(
        id="asm_001",
        statement="A technical audience trusts individual engineers more than brand channels.",
        supporting_insights=[prior_insight.id],
        current_confidence=0.95,
        risk_level=RiskLevel.LOW,
        invalidation_signals=["Skepticism about 'staged' employee content", "Fatigue with personal brand posts"]
    )
    memory.add_assumption(assumption)
    
    print("\n[INITIAL STATE]")
    print(f"Assumption: {assumption.statement}")
    print(f"Confidence: {assumption.current_confidence}")
    print(f"Risk Level: {assumption.risk_level}")
    
    # 2. Initialize Orchestrator and Agents
    orchestrator = LoopOrchestrator()
    orchestrator.register_agent(LoopStage.PLAN, PlanAgent())
    orchestrator.register_agent(LoopStage.GENERATE, GenerateAgent())
    orchestrator.register_agent(LoopStage.PUBLISH, PublishAgent())
    orchestrator.register_agent(LoopStage.OBSERVE, ObserveAgent())
    orchestrator.register_agent(LoopStage.INTERPRET, InterpretAgent())
    orchestrator.register_agent(LoopStage.ADAPT, AdaptAgent())
    
    # 3. Memory Binding Check (Failure first)
    print("\n[STAGING] Testing Mandatory Assumption Binding...")
    loop_fail = ReasoningLoop(id=str(uuid.uuid4()), org_id=org.id)
    try:
        # Context MISSING assumptions
        await orchestrator.run_next(loop_fail, {"organization": org, "narrative": narrative})
    except ValueError as e:
        print(f"  Caught Expected Error: {e}")

    # 4. Start the Full Loop
    loop = ReasoningLoop(id=str(uuid.uuid4()), org_id=org.id)
    context = {
        "organization": org,
        "narrative": narrative,
        "insights": memory.get_insights(),
        "assumptions": memory.get_assumptions() # Pass assumptions
    }
    
    print(f"\nStarting Valid Loop: {loop.id}")
    
    for _ in range(6):
        print(f"\n--- Stage: {loop.current_stage} ---")
        loop = await orchestrator.run_next(loop, context)
        step = loop.steps[-1]
        
        if step.decisions:
             print(f"  Decisions: {step.decisions}")
        
        # At ADAPT stage, record Strategy Changes and Update Memory
        if step.stage == LoopStage.ADAPT:
            contradictions = context.get("contradictions", [])
            for c in contradictions:
                # print(f"  [MEMORY UPDATE] Recording Contradiction for {c.insight_id}")
                memory.record_contradiction(c)
            
            strategy_change = context.get("strategy_change")
            if strategy_change:
                print(f"\n  [STRATEGY CHANGE EMITTED] ID: {strategy_change.id}")
                print(f"  DECISION: {strategy_change.decision}")
                print(f"  JUSTIFICATION: {strategy_change.justification}")
                memory.add_strategy_change(strategy_change)
                
            # Apply decay/risk updates to assumptions
            memory.apply_decay()
                
    # 5. Show Final State of Assumptions
    updated_assumption = memory.assumptions[assumption.id]
    print(f"\n--- FINAL ASSUMPTION STATE ---")
    print(f"Assumption: {updated_assumption.statement}")
    print(f"Confidence: {updated_assumption.current_confidence:.2f}")
    print(f"Risk Level: {updated_assumption.risk_level}")
    
    if updated_assumption.risk_level != RiskLevel.LOW:
        print("RESULT: Risk Level escalated due to contradictory signals. System is behaving correctly.")
    else:
        print("RESULT: Risk Level did not escalate. Logic check required.")
        
    # 6. Simulate Next Plan with High Risk Assumption constraint
    print("\n[STAGING] Testing Planning with High Risk Assumption...")
    # Force high risk for test
    updated_assumption.risk_level = RiskLevel.HIGH 
    loop_next = ReasoningLoop(id=str(uuid.uuid4()), org_id=org.id)
    # The run_next returns the UPDATED LOOP, so we need to inspect the last step of the updated loop
    loop_next = await orchestrator.run_next(loop_next, context)
    step_next = loop_next.steps[-1]
    
    print(f"  Start of Next Loop (Plan Decisions): {step_next.decisions}")
    if any("WARNING" in d for d in step_next.decisions):
         print("RESULT: System correctly flagged High Risk Assumption in planning.")

if __name__ == "__main__":
    asyncio.run(run_mnemosyne_v0_final_demo())
