import asyncio
import uuid
from datetime import datetime, timedelta
from typing import List

from mnemosyne.core.schemas import (
    Organization, Narrative, ReasoningLoop, LoopStage, Insight, InsightContradiction,
    Assumption, RiskLevel, StrategyChange, Comment, IntentType, EmotionalIntensity, AuthorType,
    LinkStrength
)
from mnemosyne.core.interfaces import LoopOrchestrator
from mnemosyne.memory.manager import MemoryManager
from mnemosyne.analytics.temporal import TemporalAnalyzer

# Helper to manufacture past contradictions
def create_past_contradiction(assumption_id: str, days_ago: int, delta: float, rationale: str) -> InsightContradiction:
    timestamp = datetime.utcnow() - timedelta(days=days_ago)
    return InsightContradiction(
        insight_id=assumption_id,
        source_id=f"sim_source_{days_ago}",
        rationale=rationale,
        confidence_delta=delta,
        timestamp=timestamp,
        link_strength=LinkStrength.STRONG,
        semantic_score=0.85
    )

async def run_mnemosyne_v2_demo():
    print("--- MNEMOSYNE V2: TEMPORAL INTELLIGENCE DEMO ---")
    
    # 1. Setup Memory with Scenarios
    memory = MemoryManager(storage_dir="storage_v2_demo")
    
    # Assumption A: "Old Scar"
    # Was 1.0. Hit by -0.2 (20 days ago), -0.2 (19 days ago). Stable since.
    # Current Conf: 0.60. Risk: MEDIUM.
    asm_old = Assumption(
        id="asm_old_scar",
        statement="Users prefer dark mode by default.",
        supporting_insights=[],
        current_confidence=0.60,
        risk_level=RiskLevel.MEDIUM,
        created_at=datetime.utcnow() - timedelta(days=30),
        last_validated_at=datetime.utcnow() - timedelta(days=19) # Last interaction long ago
    )
    memory.add_assumption(asm_old)
    
    # Assumption B: "Fresh Wound"
    # Was 1.0. Hit by -0.1 (3 days ago), -0.1 (2 days ago), -0.2 (1 hour ago).
    # Current Conf: 0.60. Risk: MEDIUM.
    asm_fresh = Assumption(
        id="asm_fresh_wound",
        statement="Users ignore the sidebar navigation.",
        supporting_insights=[],
        current_confidence=0.60,
        risk_level=RiskLevel.MEDIUM,
        created_at=datetime.utcnow() - timedelta(days=10),
        last_validated_at=datetime.utcnow() 
    )
    memory.add_assumption(asm_fresh)
    
    print("\n[SCENARIO STATE]")
    print(f"Assumption OLD:   Conf {asm_old.current_confidence}. (Target: Low Volatility, Stable)")
    print(f"Assumption FRESH: Conf {asm_fresh.current_confidence}. (Target: High Volatility, Degrading)")
    
    # 2. Synthesize History Logs
    # Note: MemoryManager.contradictions is where history lives. We preload it.
    history: List[InsightContradiction] = []
    
    # History for Old Scar
    history.append(create_past_contradiction("asm_old_scar", 20, 0.2, "Massive user revolt against light mode 20 days ago."))
    history.append(create_past_contradiction("asm_old_scar", 19, 0.2, "Continued fallout from light mode."))
    
    # History for Fresh Wound
    history.append(create_past_contradiction("asm_fresh_wound", 3, 0.1, "Sidebar clicks down."))
    history.append(create_past_contradiction("asm_fresh_wound", 2, 0.1, "Heatmap shows no sidebar activity."))
    history.append(create_past_contradiction("asm_fresh_wound", 0, 0.2, "User interview confirmed sidebar blindness today."))
    
    # Pre-load into memory (simulating persistence)
    for h in history:
        memory.contradictions.append(h)
        
    # 3. Analytics: Run Temporal Inference
    print("\n[RUNNING TEMPORAL ANALYSIS]")
    analyzer = TemporalAnalyzer()
    
    # Analyze Old Scar
    old_analysis = analyzer.analyze_assumption_trajectory(
        current_confidence=asm_old.current_confidence,
        created_at=asm_old.created_at,
        contradictions=[c for c in memory.contradictions if c.insight_id == "asm_old_scar"],
        lookback_days=30 # Increased to capture 20-day old events
    )
    
    # Analyze Fresh Wound
    fresh_analysis = analyzer.analyze_assumption_trajectory(
        current_confidence=asm_fresh.current_confidence,
        created_at=asm_fresh.created_at,
        contradictions=[c for c in memory.contradictions if c.insight_id == "asm_fresh_wound"],
        lookback_days=10
    )
    
    # 4. Display Results
    def report(name, analysis):
        metrics = analysis["metrics"]
        print(f"\nReport for {name}:")
        print(f"  Confidence: {analysis['trajectory'][-1].confidence:.2f}")
        print(f"  Volatility (StdDev): {metrics.volatility_score:.4f}")
        print(f"  Momentum (Delta/Day): {metrics.momentum_score:.4f}")
        print(f"  TEMPORAL STATUS: {metrics.status_label.upper()}")
        print("  Trajectory Replay:")
        for point in analysis['trajectory']:
            print(f"    {point.timestamp.strftime('%Y-%m-%d')}: {point.confidence:.2f} ({point.event_description})")

    report("OLD SCAR", old_analysis)
    report("FRESH WOUND", fresh_analysis)
    
    # 5. Verification Logic
    old_metrics = old_analysis["metrics"]
    fresh_metrics = fresh_analysis["metrics"]
    
    success = True
    if old_metrics.status_label != "Stable": 
        print(f"FAILURE: Old Scar should be Stable, but was {old_metrics.status_label}")
        success = False
    
    if fresh_metrics.status_label not in ["Degrading", "Volatile/Unstable"]:
        print(f"FAILURE: Fresh Wound should be Degrading/Volatile, but was {fresh_metrics.status_label}")
        success = False
        
    if success:
        print("\nRESULT: SUCCESS. System correctly distinguished past trauma from active collapse.")

if __name__ == "__main__":
    asyncio.run(run_mnemosyne_v2_demo())
