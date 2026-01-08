import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from ..core.schemas import (
    Organization, Narrative, ReasoningLoop, Insight, InsightContradiction, StrategyChange, Assumption, RiskLevel
)

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
        except Exception as e:
            print(f"Warning: Could not load memory: {e}")

    def add_insight(self, insight: Insight):
        self.insights[insight.id] = insight
        self._save()

    def record_contradiction(self, contradiction: InsightContradiction):
        self.contradictions.append(contradiction)
        if contradiction.insight_id in self.insights:
            insight = self.insights[contradiction.insight_id]
            # Capture the before state for StrategyChange emission elsewhere if needed
            insight.confidence = max(0.0, insight.confidence - contradiction.confidence_delta)
            insight.last_updated = datetime.utcnow()
        self._save()

    def add_strategy_change(self, change: StrategyChange):
        self.strategy_changes.append(change)
        self._save()

    def get_strategy_changes(self, insight_id: str = None) -> List[StrategyChange]:
        changes = sorted(self.strategy_changes, key=lambda x: x.timestamp)
        if insight_id:
            changes = [c for c in changes if c.insight_id == insight_id]
        return changes

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
