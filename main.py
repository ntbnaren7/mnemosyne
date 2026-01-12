import asyncio
import uuid
from datetime import datetime, timedelta
from typing import List

from mnemosyne.core.schemas import (
    Organization, Narrative, ReasoningLoop, LoopStage, Insight, InsightContradiction,
    Assumption, RiskLevel, StrategyChange, Comment, IntentType, EmotionalIntensity, AuthorType,
    LinkStrength, Override, AuthorityLevel
)
from mnemosyne.core.interfaces import LoopOrchestrator
from mnemosyne.memory.manager import MemoryManager

def user_interface_simulate_override(manager: MemoryManager, target_id: str, current_state: str):
    """Simulates a human executive intervening."""
    print(f"\n[HUMAN INTERVENTION REQUESTED]")
    print(f"Target: {target_id}")
    print(f"Current State: {current_state}")
    
    # Hardcoded simulation of human input
    override = Override(
        id=f"ovr_{uuid.uuid4().hex[:8]}",
        target_id=target_id,
        previous_state=current_state,
        override_action="Execute Plan B: Aggressive Market Entry (High Risk)",
        rationale="External funding secured. Risk appetite increased significantly. Ignoring V1 safety for this specific launch.",
        authority_level=AuthorityLevel.EXECUTIVE
    )
    
    print(f"Authority: {override.authority_level.value.upper()}")
    print(f"Mandate: {override.override_action}")
    print(f"Rationale: {override.rationale}")
    
    manager.add_override(override)
    print(">> OVERRIDE LOGGED.")

async def run_mnemosyne_v3_demo():
    print("--- MNEMOSYNE V3: GOVERNANCE & OVERRIDE DEMO ---")
    
    # 1. Setup Memory
    memory = MemoryManager(storage_dir="storage_v3_demo")
    
    # 2. System Intelligence (Simulation)
    # The system "thinks" Plan A is best based on V0/V1 logic.
    system_recommendation = "Execute Plan A: Conservative Growth (Low Risk)"
    plan_id = "plan_launch_q1"
    
    print(f"\n[SYSTEM INTELLIGENCE]")
    print(f"Based on 90% Confidence in 'Slow Markets', Mnemosyne Recommendation:")
    print(f"  -> {system_recommendation}")
    
    # 3. Check for Active Overrides (Before Execution)
    active_override = memory.get_active_override(plan_id)
    if active_override:
        print(f"  [!] Active Override Detected: {active_override.override_action}")
    else:
        print(f"  (No overrides detected. Proceeding with system logic...)")
    
    # 4. Human Intervention (The "Stop" Button)
    # The Executive decides to override the system recommendation.
    user_interface_simulate_override(memory, plan_id, system_recommendation)
    
    # 5. Re-Check Override (Execution Time)
    print(f"\n[EXECUTION PHASE]")
    final_decision = system_recommendation
    active_override = memory.get_active_override(plan_id)
    
    if active_override:
        print(f"** OVERRIDE APPLIED **")
        print(f"System Recommendation: {system_recommendation}")
        print(f"EXECUTING MANDATE: {active_override.override_action}")
        print(f"Authority: {active_override.authority_level}")
        final_decision = active_override.override_action
    
    # 6. Governance Audit (Debt Check)
    print(f"\n[GOVERNANCE AUDIT]")
    debt = memory.get_override_debt()
    print(f"Override Debt: {len(debt)} active item(s).")
    for d in debt:
        print(f"  - {d.id} on {d.target_id}: '{d.override_action}' (Rationale: {d.rationale})")

    # Verification
    if final_decision == "Execute Plan B: Aggressive Market Entry (High Risk)" and len(debt) == 1:
        print("\nRESULT: SUCCESS. Human Authority successfully overrode System Intelligence. Debt recorded.")
    else:
         print(f"\nRESULT: FAILURE. Decision was '{final_decision}'. Debt count: {len(debt)}.")

if __name__ == "__main__":
    asyncio.run(run_mnemosyne_v3_demo())
