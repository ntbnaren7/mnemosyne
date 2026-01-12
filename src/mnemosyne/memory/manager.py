import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from ..core.schemas import (
    Organization, Narrative, ReasoningLoop, Insight, InsightContradiction, StrategyChange, Assumption, RiskLevel,
    Override
)

MAX_CONFIDENCE_DROP_PER_CYCLE = 0.20

class MemoryManager:
    """
    V0 Memory Manager with simple JSON persistence and Strategic Rationale support.
    """
    def __init__(self, storage_dir: str = "storage"):
        self.storage_dir = storage_dir
        self.organizations: Dict[str, Organization] = {}
        self.narratives: Dict[str, Narrative] = {}
        self.loops: Dict[str, ReasoningLoop] = {}
        self.insights: Dict[str, Insight] = {}
        self.assumptions: Dict[str, Assumption] = {}
        self.contradictions: List[InsightContradiction] = []
        self.strategy_changes: List[StrategyChange] = []
        self.overrides: List[Override] = []
        
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
        self._load()

    def _get_path(self, name: str) -> str:
        return os.path.join(self.storage_dir, f"{name}.json")

    def _save(self):
        with open(self._get_path("organizations"), "w") as f:
            json.dump({k: v.model_dump(mode='json') for k, v in self.organizations.items()}, f, indent=2)
        with open(self._get_path("narratives"), "w") as f:
            json.dump({k: v.model_dump(mode='json') for k, v in self.narratives.items()}, f, indent=2)
        with open(self._get_path("loops"), "w") as f:
            json.dump({k: v.model_dump(mode='json') for k, v in self.loops.items()}, f, indent=2)
        with open(self._get_path("insights"), "w") as f:
            json.dump({k: v.model_dump(mode='json') for k, v in self.insights.items()}, f, indent=2)
        with open(self._get_path("contradictions"), "w") as f:
            json.dump([v.model_dump(mode='json') for v in self.contradictions], f, indent=2)
        with open(self._get_path("assumptions"), "w") as f:
            json.dump({k: v.model_dump(mode='json') for k, v in self.assumptions.items()}, f, indent=2)
        with open(self._get_path("strategy_changes"), "w") as f:
            json.dump([v.model_dump(mode='json') for v in self.strategy_changes], f, indent=2)
        with open(self._get_path("overrides"), "w") as f:
            json.dump([v.model_dump(mode='json') for v in self.overrides], f, indent=2)

    def _load(self):
        try:
            if os.path.exists(self._get_path("organizations")):
                with open(self._get_path("organizations"), "r") as f:
                    data = json.load(f)
                    self.organizations = {k: Organization(**v) for k, v in data.items()}
            if os.path.exists(self._get_path("narratives")):
                with open(self._get_path("narratives"), "r") as f:
                    data = json.load(f)
                    self.narratives = {k: Narrative(**v) for k, v in data.items()}
            if os.path.exists(self._get_path("loops")):
                with open(self._get_path("loops"), "r") as f:
                    data = json.load(f)
                    self.loops = {k: ReasoningLoop(**v) for k, v in data.items()}
            if os.path.exists(self._get_path("insights")):
                with open(self._get_path("insights"), "r") as f:
                    data = json.load(f)
                    self.insights = {k: Insight(**v) for k, v in data.items()}
            if os.path.exists(self._get_path("contradictions")):
                with open(self._get_path("contradictions"), "r") as f:
                    data = json.load(f)
                    self.contradictions = [InsightContradiction(**v) for v in data]
            if os.path.exists(self._get_path("assumptions")):
                with open(self._get_path("assumptions"), "r") as f:
                    data = json.load(f)
                    self.assumptions = {k: Assumption(**v) for k, v in data.items()}
            if os.path.exists(self._get_path("strategy_changes")):
                with open(self._get_path("strategy_changes"), "r") as f:
                    data = json.load(f)
                    self.strategy_changes = [StrategyChange(**v) for v in data]
            if os.path.exists(self._get_path("overrides")):
                with open(self._get_path("overrides"), "r") as f:
                    data = json.load(f)
                    self.overrides = [Override(**v) for v in data]
        except Exception as e:
            print(f"Warning: Could not load memory: {e}")

    def add_insight(self, insight: Insight):
        self.insights[insight.id] = insight
        self._save()

    def process_contradictions(self, contradictions: List[InsightContradiction]):
        """
        V1 Safety Rail: Processes a batch of contradictions with specific safety caps.
        Aggregates confidence drops per assumption and enforces MAX_CONFIDENCE_DROP_PER_CYCLE.
        """
        # 1. Archive raw contradictions (History Preservation)
        self.contradictions.extend(contradictions)
        
        # 2. Aggregate Deltas by ID
        active_deltas: Dict[str, float] = {}
        affected_assumptions: Dict[str, List[InsightContradiction]] = {}
        
        for c in contradictions:
            if c.insight_id not in active_deltas:
                active_deltas[c.insight_id] = 0.0
                affected_assumptions[c.insight_id] = []
            active_deltas[c.insight_id] += c.confidence_delta
            affected_assumptions[c.insight_id].append(c)
            
        # 3. Apply Updates with Safety Rail
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
        
        for a_id, total_delta in active_deltas.items():
            if a_id in self.assumptions:
                assumption = self.assumptions[a_id]
                
                # Apply Safety Cap
                final_delta = total_delta
                if final_delta > MAX_CONFIDENCE_DROP_PER_CYCLE:
                    print(f"\n[SAFETY RAIL ACTIVATED]")
                    print(f"Assumption: {a_id}")
                    print(f"Calculated Delta: -{total_delta:.2f}")
                    print(f"Capped Delta: -{MAX_CONFIDENCE_DROP_PER_CYCLE:.2f}")
                    print(f"Reason: Single-cycle confidence drop exceeded allowed maximum")
                    final_delta = MAX_CONFIDENCE_DROP_PER_CYCLE
                
                # Apply update
                assumption.current_confidence = max(0.0, assumption.current_confidence - final_delta)
                assumption.last_validated_at = datetime.utcnow()
                
                # Record Invalidating Signals (logging the cap in the signal history too)
                for c in affected_assumptions[a_id]:
                    rating = f"({c.link_strength.value})" if c.link_strength else ""
                    signal_text = f"[{timestamp}] Contradiction {rating}: {c.rationale}"
                    assumption.invalidation_signals.append(signal_text)

                if final_delta != total_delta:
                    assumption.invalidation_signals.append(f"[{timestamp}] SAFETY RAIL: Confidence drop capped at {MAX_CONFIDENCE_DROP_PER_CYCLE} (Calculated: {total_delta}).")
                    
            elif a_id in self.insights:
                # Legacy support for Insights (no explicit cap mandated, but good practice to keep distinct)
                insight = self.insights[a_id]
                insight.confidence = max(0.0, insight.confidence - total_delta)
                insight.last_updated = datetime.utcnow()
        
        self._save()

    def record_contradiction(self, contradiction: InsightContradiction):
        # Legacy Wrapper: Forward to batch processor
        self.process_contradictions([contradiction])

    def add_strategy_change(self, change: StrategyChange):
        self.strategy_changes.append(change)
        self._save()

    def get_strategy_changes(self, insight_id: str = None) -> List[StrategyChange]:
        changes = sorted(self.strategy_changes, key=lambda x: x.timestamp)
        if insight_id:
            changes = [c for c in changes if c.insight_id == insight_id]
        return changes

    def add_override(self, override: Override):
        """V3 Governance: Explicitly logs a human override."""
        # Deactivate any previous overrides for this target
        for o in self.overrides:
            if o.target_id == override.target_id and o.active:
                o.active = False
        self.overrides.append(override)
        self._save()

    def get_active_override(self, target_id: str) -> Optional[Override]:
        """Returns the active override for a target, if any."""
        for o in reversed(self.overrides):
            if o.target_id == target_id and o.active:
                return o
        return None

    def get_override_debt(self) -> List[Override]:
        """Returns all currently active overrides (Debt)."""
        return [o for o in self.overrides if o.active]

    def add_assumption(self, assumption: Assumption):
        self.assumptions[assumption.id] = assumption
        self._save()

    def get_assumptions(self) -> List[Assumption]:
        return list(self.assumptions.values())

    def apply_decay(self):
        """Apply time-based confidence decay to all insights and assumptions."""
        now = datetime.utcnow()
        for insight in self.insights.values():
            days_passed = (now - insight.last_updated).days
            if days_passed > 0:
                decay = insight.decay_rate * days_passed
                insight.confidence = max(0.0, insight.confidence - decay)
                insight.last_updated = now
        
        for assumption in self.assumptions.values():
            days_passed = (now - assumption.last_validated_at).days
            if days_passed > 0:
                decay = assumption.decay_rate * days_passed
                assumption.current_confidence = max(0.0, assumption.current_confidence - decay)
                assumption.last_validated_at = now
                
                # Update Risk Level based on confidence
                if assumption.current_confidence < 0.4:
                    assumption.risk_level = RiskLevel.HIGH
                elif assumption.current_confidence < 0.7:
                    assumption.risk_level = RiskLevel.MEDIUM
                else:
                    assumption.risk_level = RiskLevel.LOW
                    
        self._save()

    def get_insights(self) -> List[Insight]:
        return list(self.insights.values())

    def add_organization(self, org: Organization):
        self.organizations[org.id] = org
        self._save()

    def add_narrative(self, narrative: Narrative):
        self.narratives[narrative.id] = narrative
        self._save()

    def get_active_narrative(self, org_id: str) -> Optional[Narrative]:
        for n in self.narratives.values():
            if n.org_id == org_id and n.active:
                return n
        return None

    def store_loop(self, loop: ReasoningLoop):
        self.loops[loop.id] = loop
        self._save()

    def get_loop(self, loop_id: str) -> Optional[ReasoningLoop]:
        return self.loops.get(loop_id)
