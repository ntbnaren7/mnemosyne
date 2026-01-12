from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from pydantic import BaseModel
import statistics
import math

# Re-import Core Schemas to avoid Circular Import Issues issues down the line?
# For now, we only need basic types, and we accept Assumption/InsightContradiction as dicts or objects.
# To stay clean, we will assume pass-by-reference of the memory objects.

class TrajectoryPoint(BaseModel):
    """Snapshot of a belief state at a specific time."""
    timestamp: datetime
    confidence: float
    event_description: str

class TrajectoryMetrics(BaseModel):
    """Derived temporal signals."""
    volatility_score: float # Standard deviation of changes
    momentum_score: float   # Average daily confidence velocity
    status_label: str       # "Stable", "Degrading", "Collapsing", "Recovering"
    
class TemporalAnalyzer:
    """
    Read-only analytics engine that reconstructs belief trajectories.
    Does NOT modify beliefs.
    """
    
    def analyze_assumption_trajectory(
        self, 
        current_confidence: float, 
        created_at: datetime,
        contradictions: List[Any], # List[InsightContradiction]
        lookback_days: int = 30
    ) -> Dict[str, Any]:
        """
        Reconstructs the confidence path over time by replaying history.
        Note: Since we store current state and have a log of *deltas*, 
        we can work backwards or forwards if we knew the start. 
        Working backwards from current is often safer for immediate history.
        """
        
        # 1. Sort events descending (newest first)
        sorted_events = sorted(
            [c for c in contradictions], 
            key=lambda x: x.timestamp, 
            reverse=True
        )
        
        now = datetime.utcnow()
        cutoff = now - timedelta(days=lookback_days)
        
        # 2. Reconstruct Timeline (Backwards)
        timeline: List[TrajectoryPoint] = []
        running_conf = current_confidence
        
        # Point: Now
        timeline.append(TrajectoryPoint(
            timestamp=now, 
            confidence=running_conf, 
            event_description="Current State"
        ))
        
        relevant_events = [e for e in sorted_events if e.timestamp >= cutoff]
        
        for event in relevant_events:
            # If we are at state X, and event dropped delta D, prev state was X + D
            # Note: This ignores decay for simplicity in V2, focusing on event-driven volatility.
            # Ideally we'd account for decay, but since decay is continuous and log-less, we approximate.
            prev_conf = min(1.0, running_conf + event.confidence_delta)
            
            timeline.append(TrajectoryPoint(
                timestamp=event.timestamp,
                confidence=prev_conf,
                event_description=f"Before Contradiction: {event.rationale[:30]}..."
            ))
            running_conf = prev_conf
            
        # Re-sort timeline chronological for analysis
        timeline.sort(key=lambda x: x.timestamp)
        
        # 3. Calculate Metrics
        metrics = self._calculate_metrics(timeline, current_confidence)
        
        return {
            "trajectory": timeline,
            "metrics": metrics
        }
        
    def _calculate_metrics(self, timeline: List[TrajectoryPoint], current_conf: float) -> TrajectoryMetrics:
        if len(timeline) < 2:
            return TrajectoryMetrics(
                volatility_score=0.0,
                momentum_score=0.0,
                status_label="Stable (New)"
            )
            
        # Velocity Steps
        deltas = []
        for i in range(1, len(timeline)):
            # diff = later - earlier
            diff = timeline[i].confidence - timeline[i-1].confidence
            deltas.append(diff)
            
        # Volatility: Std Dev of these event-driven jumps
        if len(deltas) > 1:
            volatility = statistics.stdev(deltas)
        else:
            volatility = abs(deltas[0]) if deltas else 0.0
            
        # Momentum: Net change / Time
        start_time = timeline[0].timestamp
        end_time = timeline[-1].timestamp
        duration_days = (end_time - start_time).days
        if duration_days < 1: 
            duration_days = 1
            
        net_change = current_conf - timeline[0].confidence
        momentum = net_change / duration_days
        
        # Labeling (Heuristic for V2)
        if volatility > 0.15:
            status = "Volatile/Unstable"
        elif momentum < -0.05:
            status = "Degrading"
        elif momentum > 0.05:
            status = "Recovering"
        else:
            status = "Stable"
            
        return TrajectoryMetrics(
            volatility_score=volatility,
            momentum_score=momentum,
            status_label=status
        )
