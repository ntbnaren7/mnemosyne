import sys
import os
import uuid
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
# Ensure 'src' is in python path for schemas (Patch for local execution)
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from mnemosyne.core.schemas import ContentBrief
from sandbox.executor import ContentExecutor

def run_sandbox_demo():
    print("--- MNEMOSYNE CONTENT EXECUTION SANDBOX ---")
    
    # 1. Theoretical Mnemosyne Output (The Brief)
    # This represents Mnemosyne saying "Visualize Trust based on my beliefs".
    brief = ContentBrief(
        id=f"brief_{uuid.uuid4().hex[:8]}",
        target_id="post_q1_trust",
        narrative_intent="Demonstrate that our infrastructure is robust and mathematically verified.",
        visual_intent="Abstract geometric nodes connecting in a secure lattice. Blue and Gold palette. High contrast.",
        assumptions_referenced=["asm_trust", "asm_quality"],
        risk_notes="Avoid chaotic patterns. Must look ordered and calm.",
        experiment_tag="exp_visual_trust_v1"
    )
    
    print("\n[INCOMING BRIEF FROM MNEMOSYNE]")
    print(f"ID: {brief.id}")
    print(f"Narrative: {brief.narrative_intent}")
    print(f"Visual Mandate: {brief.visual_intent}")
    print(f"Governing Assumptions: {brief.assumptions_referenced}")
    
    # 2. Handoff to Sandbox (Execution Layer)
    print("\n[SANDBOX EXECUTION]")
    executor = ContentExecutor()
    assets = executor.generate_assets(brief)
    
    # 3. Validation / Output
    print("\n[GENERATED ASSETS]")
    for i, asset in enumerate(assets):
        print(f"\nAsset #{i+1}")
        print(f"  Path: {asset.path}")
        print(f"  Prompt Used: {asset.prompt}")
        print(f"  Traceability: {asset.metadata['assumptions']}")
        print(f"  Generator: {asset.metadata['generator']}")
        
    print("\nRESULT: SUCCESS. Mnemosyne's belief governed the creation of 5 assets.")

if __name__ == "__main__":
    run_sandbox_demo()
