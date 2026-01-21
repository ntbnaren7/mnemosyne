from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

# Import core types to ensure compatibility (acting as the connection to the "Brain")
from src.mnemosyne.core.schemas import Assumption, RiskLevel

class CompanyStage(str, Enum):
    STARTUP = "startup"
    SCALEUP = "scaleup"
    ENTERPRISE = "enterprise"

class TonePreference(str, Enum):
    PROFESSIONAL = "professional"
    WITTY = "witty"
    EMPATHETIC = "empathetic"
    AUTHORITATIVE = "authoritative"
    INNOVATIVE = "innovative"

class CompanyContext(BaseModel):
    name: str
    industry: str
    description: str
    stage: CompanyStage
    tone: TonePreference
    posting_frequency_per_week: int = Field(default=2, ge=1, le=7)
    target_audience: List[str]

class PostObjective(str, Enum):
    BRAND_AWARENESS = "brand_awareness"
    PRODUCT_EDUCATION = "product_education"
    HIRING_CULTURE = "hiring_culture"
    THOUGHT_LEADERSHIP = "thought_leadership"

class PostBrief(BaseModel):
    """
    A semantic plan for a single post.
    Does NOT contain the actual prompt, but contains the ingredients for it.
    """
    id: str
    week_number: int # 1-4
    scheduled_date: datetime
    objective: PostObjective
    
    # Connection to Mnemosyne Core
    governing_assumptions: List[Assumption]
    risk_notes: str # Assessment of risk for this specific topic
    
    hypothesis: str # Why do we think this post will work?
    
    # Semantic content attributes
    topic: str
    key_message: str
    visual_direction: str # "Minimialist tech" (semantic, not prompt)
    caption_intent: str

class MonthPlan(BaseModel):
    month_name: str
    year: int
    company_context: CompanyContext
    posts: List[PostBrief]
    generated_at: datetime = Field(default_factory=datetime.utcnow)
