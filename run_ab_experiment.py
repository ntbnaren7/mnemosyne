import sys
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()

# Ensure 'src' is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from mnemosyne.core.schemas import ContentBrief
from sandbox.experiment import BeliefToggleExperiment
from sandbox.executor import ContentExecutor

def run_ab_experiment():
    print("--- MNEMOSYNE A/B BELIEF TOGGLE EXPERIMENT ---")
    
    # 0. Define the Experiment Primitive
    experiment = BeliefToggleExperiment(
        id=f"exp_{uuid.uuid4().hex[:8]}",
        baseline_assumption_id="asm_chaos_trust",
        variant_assumption_id="asm_order_trust",
        narrative_context="Launch of new API Platform"
    )
    print(f"\n[EXPERIMENT SETUP]: {experiment.id}")
    print(f"Narrative: {experiment.narrative_context}")
    
    # 1. Arm A: Baseline (Chaos)
    # Belief: "Engineers trust raw complexity and visible wiring."
    brief_a = ContentBrief(
        id=f"brief_a_{uuid.uuid4().hex[:8]}",
        target_id="post_launch_A",
        narrative_intent=experiment.narrative_context,
        visual_intent="High-tech server room, glowing lights, server racks.",
        assumptions_referenced=[experiment.baseline_assumption_id],
        risk_notes="Ensure complexity is visible. Do not hide the wires. Show the mess. Authentic engineering reality.",
        experiment_tag=experiment.id
    )
    
    # 2. Arm B: Variant (Order)
    # Belief: "Engineers trust clean, minimalistic abstraction."
    brief_b = ContentBrief(
        id=f"brief_b_{uuid.uuid4().hex[:8]}",
        target_id="post_launch_B",
        narrative_intent=experiment.narrative_context,
        visual_intent="High-tech server room, glowing lights, server racks.",
        assumptions_referenced=[experiment.variant_assumption_id],
        risk_notes="Hide all complexity. Minimalist. Zen-like. No visible wires. Clean abstraction.",
        experiment_tag=experiment.id
    )
    
    executor = ContentExecutor()
    
    # 3. Execute Arm A
    print(f"\n[EXECUTING ARM A] (Assumption: {experiment.baseline_assumption_id})")
    print(f"Risk Mandate: {brief_a.risk_notes}")
    assets_a = executor.generate_assets(brief_a)
    
    # 4. Execute Arm B
    print(f"\n[EXECUTING ARM B] (Assumption: {experiment.variant_assumption_id})")
    print(f"Risk Mandate: {brief_b.risk_notes}")
    assets_b = executor.generate_assets(brief_b)
    
    # 5. Final Report
    print(f"\n=== FINAL REPORT: {experiment.id} ===")
    
    print(f"\nARM A RESULTS ({experiment.baseline_assumption_id}):")
    for a in assets_a:
        print(f"  - {a.path} (Trace: {a.metadata['assumptions']})")
        # print(f"    Prompt: {a.prompt}") 
        # (Omitting full prompt for brevity in final report, but it exists in object)

    print(f"\nARM B RESULTS ({experiment.variant_assumption_id}):")
    for b in assets_b:
        print(f"  - {b.path} (Trace: {b.metadata['assumptions']})")
    
    print(f"\nCONCLUSION:")
    print("These outputs differ ONLY because the governing belief changed.")
    print("Visual Intent was constant. Narrative was constant.")
    print("Assumption A -> 'Show the mess'")
    print("Assumption B -> 'No visible wires'")

if __name__ == "__main__":
    run_ab_experiment()
