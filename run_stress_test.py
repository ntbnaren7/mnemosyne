import sys
import os
import uuid
import shutil
from datetime import datetime

# Ensure 'src' is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from mnemosyne.core.schemas import Assumption, RiskLevel, LinkStrength, InsightContradiction
from mnemosyne.memory.manager import MemoryManager
from mnemosyne.core.semantic import SemanticEngine

def run_stress_test():
    print("--- MNEMOSYNE BELIEF STRESS TEST ---")
    
    # Setup Verification Storage
    storage_dir = "storage_stress_test"
    if os.path.exists(storage_dir):
        shutil.rmtree(storage_dir)
    
    # 1. Initialize Core Engines
    print("\n[INIT] Initializing V0 Memory & V1 Semantic Engine...")
    memory = MemoryManager(storage_dir=storage_dir)
    engine = SemanticEngine()
    
    # 2. Seed Conflicting Assumptions
    print("\n[SEEDING] Creating Competing Beliefs...")
    
    # Assumption A: Chaos
    text_chaos = "Engineers trust visible complexity and exposed systems."
    asm_chaos = Assumption(
        id="asm_chaos_trust", 
        statement=text_chaos, 
        supporting_insights=[],
        embedding=engine.encode(text_chaos)
    )
    
    # Assumption B: Order
    text_order = "Engineers trust clarity, minimalism, and hidden complexity."
    asm_order = Assumption(
        id="asm_order_trust",
        statement=text_order,
        supporting_insights=[],
        embedding=engine.encode(text_order)
    )
    
    memory.add_assumption(asm_chaos)
    memory.add_assumption(asm_order)
    
    print(f"  > Seeding: {asm_chaos.id} (Conf: {asm_chaos.current_confidence})")
    print(f"  > Seeding: {asm_order.id} (Conf: {asm_order.current_confidence})")
    
    # 3. Round 1: Baseline State
    print("\n[ROUND 1: BASELINE]")
    print(f"  {asm_chaos.id}: Confidence {asm_chaos.current_confidence}")
    print(f"  {asm_order.id}: Confidence {asm_order.current_confidence}")
    
    # 4. Feedback Injection
    print("\n[FEEDBACK INJECTION]")
    # Simulated user feedback on the "Chaos" arm generated images
    feedback_signals = [
        "This visual feels too messy and hard to parse.",
        "It is overwhelming and confusing to look at.",
        "I don't trust this, it looks like broken code.",
        "Too much complexity, I want to see the high level.",
        "Cluttered and chaotic, not professional."
    ]
    
    contradictions = []
    
    for signal in feedback_signals:
        print(f"  > Signal: '{signal}'")
        emb_signal = engine.encode(signal)
        
        # Check against Chaos Assumption
        sim_chaos = engine.similarity(emb_signal, asm_chaos.embedding)
        
        # In V1 logic, high similarity between a "Critique" and an Assumption means the critique TARGETS it.
        # But we need to know if the signal SUPPORTS or OPPOSES.
        # For this test, we assume the signals are NEGATIVE sentiment (Critiques).
        # So high semantic overlap = Strong Contradiction.
        
        # Note: In a real loop, InterpretAgent determines Intent (Critique) first.
        # Here we hardcode Intent=Critique.
        
        if sim_chaos > 0.25:
            strength = LinkStrength.WEAK
            delta = 0.02
            if sim_chaos > 0.4:
                strength = LinkStrength.MODERATE
                delta = 0.08
            if sim_chaos > 0.6:
                strength = LinkStrength.STRONG
                delta = 0.15
            
            print(f"    -> Targets {asm_chaos.id} (Sim: {sim_chaos:.2f} | {strength.name})")
            
            c = InsightContradiction(
                insight_id=asm_chaos.id,
                source_id="simulated_feedback",
                rationale=f"User feedback '{signal}' contradicts belief in visible complexity.",
                confidence_delta=delta,
                link_strength=strength,
                semantic_score=sim_chaos
            )
            contradictions.append(c)
        else:
             print(f"    -> (No Link to {asm_chaos.id})")

    # 5. Process Updates (Adaptation)
    print("\n[ADAPTATION PHASE]")
    print(f"  Processing {len(contradictions)} contradictions...")
    memory.process_contradictions(contradictions)
    
    # 6. Round 2: Final State
    updated_chaos = memory.assumptions["asm_chaos_trust"]
    updated_order = memory.assumptions["asm_order_trust"]
    
    print("\n[ROUND 2: RESULT]")
    print(f"  {updated_chaos.id}: Confidence {updated_chaos.current_confidence:.2f} (Delta: {updated_chaos.current_confidence - 1.0:.2f})")
    print(f"  {updated_order.id}: Confidence {updated_order.current_confidence:.2f} (Delta: {updated_order.current_confidence - 1.0:.2f})")
    
    # Check for Safety Rail Trace
    for note in updated_chaos.invalidation_signals:
        if "SAFETY RAIL" in note:
            print(f"  ! SAFETY RAIL ACTIVATED: {note}")

    print("\n[EXPLANATION]")
    print("Optimization observed: The belief in 'visible complexity' failed to resonate with users.")
    print("Mnemosyne has reduced confidence in asm_chaos_trust while retaining asm_order_trust.")
    print("Future content will skew towards Order.")
    
    if updated_chaos.current_confidence < 1.0 and updated_order.current_confidence == 1.0:
        print("\nRESULT: SUCCESS. Mnemosyne adapted its beliefs based on semantic feedback.")
    else:
        print("\nRESULT: FAILURE. Beliefs did not adapt as expected.")

if __name__ == "__main__":
    run_stress_test()
