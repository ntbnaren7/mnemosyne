import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class LoopStage(str, Enum):
    PLAN = "PLAN"
    GENERATE = "GENERATE"
    PUBLISH = "PUBLISH"
    OBSERVE = "OBSERVE"
    INTERPRET = "INTERPRET"
    ADAPT = "ADAPT"

class AuthorType(str, Enum):
    EMPLOYEE = "employee"
    CANDIDATE = "candidate"
    CUSTOMER = "customer"
    UNKNOWN = "unknown"

class IntentType(str, Enum):
    QUESTION = "question"
    CRITIQUE = "critique"
    PRAISE = "praise"
    SPAM = "spam"

class EmotionalIntensity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class LinkStrength(str, Enum):
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Assumption(BaseModel):
    """An active bet the system is making, with associated risk."""
    id: str
    statement: str
    supporting_insights: List[str]  # Insight IDs
    current_confidence: float = 1.0  # 0.0 to 1.0
    risk_level: RiskLevel = RiskLevel.LOW
    last_validated_at: datetime = Field(default_factory=datetime.utcnow)
    invalidation_signals: List[str] = [] # Human-readable descriptions of what would break this
    created_at: datetime = Field(default_factory=datetime.utcnow)
    decay_rate: float = 0.01
    embedding: Optional[List[float]] = None # V1 Semantic Vector

class Insight(BaseModel):
    """A strategic belief derived from interpretations."""
    id: str
    content: str
    confidence: float = 1.0  # 0.0 to 1.0
    source_loop_ids: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    decay_rate: float = 0.01  # Amount to decay per day or signal

class InsightContradiction(BaseModel):
    """Records an event where new data opposes an insight or assumption."""
    insight_id: str
    source_id: str  # e.g., Comment ID or Loop ID
    rationale: str
    confidence_delta: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    link_strength: Optional[LinkStrength] = None # V1 Semantic Link Strength
    semantic_score: Optional[float] = None # V1 Similarity score

class StrategyChange(BaseModel):
    """A first-class record of a strategic pivot or adjustment."""
    id: str = Field(default_factory=lambda: f"sc_{uuid.uuid4().hex[:8]}")
    insight_id: Optional[str] = None
    related_assumption_ids: List[str] = [] # Assumptions modified by this change
    previous_assumption: str
    triggering_signals: List[str]
    confidence_from: float
    confidence_to: float
    decision: str
    justification: str
    acknowledged_risks: List[str]
    review_horizon: datetime
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Organization(BaseModel):
    """Represents the strategic identity of a company/entity."""
    id: str
    name: str
    mission: str
    core_values: List[str]
    target_audience: List[str]
    strategic_priorities: List[str]

class Narrative(BaseModel):
    """Current strategic theme or story being told."""
    id: str
    org_id: str
    title: str
    objectives: List[str]
    key_messages: List[str]
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Creative(BaseModel):
    """Metadata for visual or creative assets."""
    id: str
    type: str  # e.g., "image", "video"
    attributes: Dict[str, Any]  # Explicit visual attributes, not vibes
    prompt_metadata: Optional[str] = None
    url: Optional[str] = None

class Post(BaseModel):
    """A single piece of content within a narrative."""
    id: str
    narrative_id: str
    content_text: str
    creatives: List[Creative] = []
    platform: str
    status: str = "draft"
    scheduled_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

class Comment(BaseModel):
    """Engagement signals containing high-signal feedback."""
    id: str
    post_id: str
    author: str
    author_type: AuthorType = AuthorType.UNKNOWN
    content: str
    intent: IntentType = IntentType.QUESTION
    topic_cluster: Optional[str] = None
    emotional_intensity: EmotionalIntensity = EmotionalIntensity.LOW
    sentiment_score: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    embedding: Optional[List[float]] = None # V1 Semantic Vector

class Performance(BaseModel):
    """Raw metrics and initial interpretation."""
    post_id: str
    metrics: Dict[str, int]  # e.g., {"likes": 10, "shares": 2, "comments": 5}
    raw_signals: List[Dict[str, Any]]
    interpreted_at: datetime = Field(default_factory=datetime.utcnow)

class ReasoningStep(BaseModel):
    """A single step in the reasoning loop."""
    stage: LoopStage
    intent: str
    context_used: List[str]  # IDs of narratives, posts, etc.
    referenced_insights: List[str] = [] # Required for PLAN
    referenced_assumptions: List[str] = [] # Required for PLAN (primitive V0 assumption)
    memory_override_reason: Optional[str] = None # Alternative for PLAN
    strategy_change_id: Optional[str] = None # Emitted during ADAPT
    hypothesis: Optional[str] = None
    decisions: List[str]
    rationale: str
    human_approved: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ReasoningLoop(BaseModel):
    """The full lifecycle of a strategic decision."""
    id: str
    org_id: str
    steps: List[ReasoningStep] = []
    current_stage: LoopStage = LoopStage.PLAN
