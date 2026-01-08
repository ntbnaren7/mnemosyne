import uuid
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from ..core.schemas import (
    Organization, Narrative, Assumption, RiskLevel, 
    ReasoningLoop, LoopStage, VisualIntent, Post, Creative
)
from ..core.interfaces import LoopOrchestrator
from ..loop.agents import (
    PlanAgent, GenerateAgent, PublishAgent, 
    ObserveAgent, InterpretAgent, AdaptAgent
)
from ..memory.manager import MemoryManager

class BundleGenerator:
    """
    Orchestrates the frozen core agents to generate a monthly bundle of content.
    Research POC Layer.
    """
    def __init__(self, storage_dir="storage_poc"):
        self.memory = MemoryManager(storage_dir=storage_dir)
        self.orchestrator = LoopOrchestrator()
        self._register_agents()
        
    def _register_agents(self):
        self.orchestrator.register_agent(LoopStage.PLAN, PlanAgent())
        self.orchestrator.register_agent(LoopStage.GENERATE, GenerateAgent())
        self.orchestrator.register_agent(LoopStage.PUBLISH, PublishAgent())
        # Observe/Interpret/Adapt not used for generation flow, but registered for completeness
        self.orchestrator.register_agent(LoopStage.OBSERVE, ObserveAgent())
        self.orchestrator.register_agent(LoopStage.INTERPRET, InterpretAgent())
        self.orchestrator.register_agent(LoopStage.ADAPT, AdaptAgent())

    async def generate_monthly_bundle(self, 
                                      company_name: str, 
                                      industry: str, 
                                      description: str, 
                                      goal: str, 
                                      num_posts: int = 4) -> Dict[str, Any]:
        
        # 1. Setup Company Context (Org, Narrative, Assumption)
        org_id = f"org_{uuid.uuid4().hex[:8]}"
        org = Organization(
            id=org_id,
            name=company_name,
            mission=description,
            core_values=[goal, "Innovation", "Trust"], # Mock values based on goal
            target_audience=["Professionals", "Decision Makers"],
            strategic_priorities=[f"Establish leadership in {industry}"]
        )
        self.memory.add_organization(org)
        
        narrative = Narrative(
            id=f"narr_{uuid.uuid4().hex[:8]}",
            org_id=org_id,
            title=f"The Future of {industry}",
            objectives=[goal],
            key_messages=[f"{company_name} is leading the way.", "Innovation matters."]
        )
        self.memory.add_narrative(narrative)
        
        # Seed an Assumption (Required for PlanAgent V0)
        assumption = Assumption(
            id=f"asm_{uuid.uuid4().hex[:8]}",
            statement=f"The {industry} market values transparency and technical depth.",
            supporting_insights=[],
            current_confidence=0.8,
            risk_level=RiskLevel.LOW
        )
        self.memory.add_assumption(assumption)
        
        # 2. Strategic Planning (Run PlanAgent)
        plan_loop = ReasoningLoop(id=f"loop_plan_{uuid.uuid4().hex[:8]}", org_id=org_id)
        context = {
            "organization": org,
            "narrative": narrative,
            "insights": [],
            "assumptions": [assumption]
        }
        
        # Run PLAN stage
        plan_loop = await self.orchestrator.run_next(plan_loop, context)
        plan_step = plan_loop.steps[-1]
        strategy_summary = f"Focus: {goal}. Assumed: {assumption.statement}"
        
        # 3. Generate Posts (Fixed 5-Post Logic for CEO Demo)
        from .renderer import SmartRenderer
        smart_renderer = SmartRenderer()
        
        posts_data = []
        start_date = datetime.now() + timedelta(days=2)
        
        # Fixed Schedule Definition
        # 1. Brand Awareness (Text-led Brand Card)
        # 2. SaaS Transparency (Abstract Diagram)
        # 3. Brand Awareness (Text-led Brand Card)
        # 4. Hiring (Human Illustration)
        # 5. Brand Vision (Text-led Brand Card)
        
        fixed_schedule = [
            {
                "intent_tag": "Brand Awareness",
                "visual_style": "minimal", 
                "composition": "text_led", 
                "human_presence": "none",
                "headline": f"Why {company_name} Stands Apart",
                "content_stub": f"In a crowded market, clarity is power. {company_name} is redefining how {industry} leaders access intelligence."
            },
            {
                "intent_tag": "SaaS / AI Transparency",
                "visual_style": "abstract", 
                "composition": "subject_centered", 
                "human_presence": "none",
                "headline": "Under the Hood: Core Architecture",
                "content_stub": "Trust requires transparency. A look at the real-time processing layer driving our latest insights model."
            },
            {
                "intent_tag": "Brand Awareness",
                "visual_style": "minimal", 
                "composition": "text_led", 
                "human_presence": "none",
                "headline": "Strategic Clarity for 2026",
                "content_stub": f"The landscape of {industry} is shifting. We help you navigate the noise with precision."
            },
            {
                "intent_tag": "Hiring / Trust",
                "visual_style": "illustrative", 
                "composition": "subject_centered", 
                "human_presence": "explicit",
                "headline": "Join the Builders",
                "content_stub": f"We are looking for engineers who care about {industry}. Come build the future with us."
            },
            {
                "intent_tag": "Brand Vision",
                "visual_style": "minimal", 
                "composition": "text_led", 
                "human_presence": "none",
                "headline": "The Future is Transparent",
                "content_stub": "Our vision is simple: Democratize access to strategic truth. Thank you for being part of the journey."
            }
        ]
        
        for i, item in enumerate(fixed_schedule):
            # Create Loop artifact (Mock context)
            visual_intent = VisualIntent(
                visual_style=item["visual_style"],
                composition=item["composition"],
                human_presence=item["human_presence"],
                face_count="0" if item["human_presence"] == "none" else "1-2"
            )
            
            # --- RENDER ---
            # Call SmartRenderer with intent + headline
            image_artifact = await smart_renderer.render(
                intent=visual_intent,
                headline=item["headline"]
            )
            
            post_content = f"#{i+1} [{item['intent_tag']}] {item['content_stub']} #Growth #{company_name}"
            post_date = start_date + timedelta(days=i*3)
            
            posts_data.append({
                "date": post_date.strftime("%Y-%m-%d"),
                "intent": item['intent_tag'],
                "content": post_content,
                "image_artifact": image_artifact,
                "visual_intent": visual_intent
            })
            
        return {
            "organization": org,
            "strategy_snapshot": strategy_summary,
            "assumptions": [assumption],
            "posts": posts_data
        }

    def _get_varied_visual_intent(self, index: int, industry: str) -> VisualIntent:
        # Deprecated for CEO Demo
        pass
