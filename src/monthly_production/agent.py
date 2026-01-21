import random
import uuid
from datetime import datetime, timedelta
from typing import List

from .schemas import CompanyContext, MonthPlan, PostBrief, PostObjective, CompanyStage, TonePreference
from src.mnemosyne.memory.manager import MemoryManager
from src.mnemosyne.core.schemas import Assumption, RiskLevel

class MonthlyProductionAgent:
    def __init__(self, storage_dir: str = "storage"):
        self.memory = MemoryManager(storage_dir=storage_dir)
        # Ensure we have some assumptions to work with if empty (Prototype convenience)
        if not self.memory.get_assumptions():
            self._seed_default_assumptions()

    def _seed_default_assumptions(self):
        """Seed some default assumptions if the brain is empty, so the prototype works."""
        defaults = [
            Assumption(
                id="asm_trust",
                statement="Users trust transparent communication over polished marketing.",
                supporting_insights=[],
                risk_level=RiskLevel.LOW
            ),
            Assumption(
                id="asm_visual",
                statement="High-contrast, dark-mode visuals signal 'premium' to tech audiences.",
                supporting_insights=[],
                risk_level=RiskLevel.MEDIUM
            ),
            Assumption(
                id="asm_frequency",
                statement="Consistency matters more than viral spikes for B2B retention.",
                supporting_insights=[],
                risk_level=RiskLevel.LOW
            )
        ]
        for asm in defaults:
            self.memory.add_assumption(asm)

    def _select_governing_assumptions(self, objective: PostObjective) -> List[Assumption]:
        """
        Selects assumptions that should govern a specific post.
        In a full system, this would use semantic search.
        For this prototype, we select based on simple heuristics or random valid subsets.
        """
        all_assumptions = self.memory.get_assumptions()
        if not all_assumptions:
            return []
        
        # Simple heuristic: heavily weight low-risk assumptions for Brand Awareness
        if objective == PostObjective.BRAND_AWARENESS:
            candidates = [a for a in all_assumptions if a.risk_level == RiskLevel.LOW]
        else:
            candidates = all_assumptions
            
        if not candidates:
            candidates = all_assumptions

        # Return 1 or 2 assumptions
        return random.sample(candidates, k=min(len(candidates), 2))

    def _generate_post_topics(self, context: CompanyContext, weeks: int = 5) -> List[dict]:
        """
        Generates high-level topics/objectives for the month.
        """
        # Mix varies by stage
        if context.stage == CompanyStage.STARTUP:
            # Startup: Focus on Product Education & Brand Awareness
            mix = [PostObjective.PRODUCT_EDUCATION, PostObjective.BRAND_AWARENESS, PostObjective.PRODUCT_EDUCATION, PostObjective.HIRING_CULTURE, PostObjective.THOUGHT_LEADERSHIP]
        elif context.stage == CompanyStage.SCALEUP:
            # Scaleup: Proof points, hiring, thought leadership
            mix = [PostObjective.THOUGHT_LEADERSHIP, PostObjective.HIRING_CULTURE, PostObjective.PRODUCT_EDUCATION, PostObjective.BRAND_AWARENESS, PostObjective.THOUGHT_LEADERSHIP]
        else:
            # Enterprise: Brand safety, leadership, culture
            mix = [PostObjective.BRAND_AWARENESS, PostObjective.THOUGHT_LEADERSHIP, PostObjective.HIRING_CULTURE, PostObjective.BRAND_AWARENESS, PostObjective.THOUGHT_LEADERSHIP]
            
        # Adjust for length (slice or cycle)
        final_mix = (mix * 2)[:weeks]
        return final_mix

    def generate_month_plan(self, context: CompanyContext) -> MonthPlan:
        """
        Orchestrates the creation of a manufacturing plan for the month.
        """
        posts: List[PostBrief] = []
        objectives = self._generate_post_topics(context)
        
        today = datetime.utcnow()
        # Start next Monday
        days_ahead = 7 - today.weekday()
        start_date = today + timedelta(days=days_ahead)
        
        for i, objective in enumerate(objectives):
            week_num = i + 1
            scheduled_date = start_date + timedelta(weeks=i)
            
            # 1. Select Governance
            assumptions = self._select_governing_assumptions(objective)
            
            # 2. Synthesize Risk
            risk_notes = f"Governed by {len(assumptions)} assumption(s). " + " ".join([f"({a.risk_level.value.upper()}) {a.statement}" for a in assumptions])
            
            # 3. Formulate Hypothesis
            hypothesis = f"By focusing on {objective.value.replace('_', ' ')} aligned with our belief that '{assumptions[0].statement if assumptions else '...' }', we will drive engagement with {random.choice(context.target_audience)}."
            
            # 4. Create Semantic Brief (NOT A PROMPT) - WITH VARIANCE
            # Add specific angles based on objective types to avoid duplicates
            if objective == PostObjective.BRAND_AWARENESS:
                topic_angle = random.choice([
                    f"The future of {context.industry}",
                    f"Why {context.name} exists",
                    f"A day in the life at {context.name}",
                    f"Celebrating {context.industry} innovation"
                ])
                visual_style = f"Cinematic, wide-angle shot showing scale and impact of {context.industry}."
            elif objective == PostObjective.PRODUCT_EDUCATION:
                topic_angle = random.choice([
                    f"How our technology solves {random.choice(['inefficiency', 'cost', 'complexity'])}",
                    f"Deep dive into a core feature",
                    "Customer success story visualization",
                    "Technical breakdown of our architecture"
                ])
                visual_style = f"Macro photography, detailed, sleek interface elements, high-tech glow, {context.tone.value} lighting."
            elif objective == PostObjective.HIRING_CULTURE:
                topic_angle = random.choice([
                    "Our engineering team culture",
                    "Workspace and collaboration",
                    "Employee spotlight",
                    "Join our mission"
                ])
                visual_style = f"Candid, warm, natural lighting, diverse team collaborating, authentic {context.tone.value} vibe."
            elif objective == PostObjective.THOUGHT_LEADERSHIP:
                topic_angle = random.choice([
                    f"Trend analysis: {datetime.utcnow().year + 1} predictions",
                    f"The state of {context.industry} regulation",
                    "Contrarian take on current best practices",
                    "Keynote takeaway"
                ])
                visual_style = f"Minimalist, editorial, bold typography, abstract representation of {context.industry} data."
            else:
                 topic_angle = f"{objective.value} focus"
                 visual_style = f"Standard {context.name} branding."

            topic = f"{topic_angle} for {context.name} ({context.industry})"
            visual_direction = f"{visual_style} branded matching {context.name}'s {context.tone.value} tone."
            
            post = PostBrief(
                id=f"post_{uuid.uuid4().hex[:8]}",
                week_number=week_num,
                scheduled_date=scheduled_date,
                objective=objective,
                governing_assumptions=assumptions,
                risk_notes=risk_notes,
                hypothesis=hypothesis,
                topic=topic,
                key_message=f"Key message about {topic_angle}.",
                visual_direction=visual_direction,
                caption_intent=f"Write a {context.tone.value} caption about {topic_angle}."
            )
            posts.append(post)

        return MonthPlan(
            month_name=start_date.strftime("%B"),
            year=start_date.year,
            company_context=context,
            posts=posts
        )
