from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class BeliefToggleExperiment(BaseModel):
    """
    Primitive for controlling A/B belief experiments in the Sandbox.
    NOT part of the Core Memory.
    """
    id: str
    baseline_assumption_id: str
    variant_assumption_id: str
    narrative_context: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "PENDING"
