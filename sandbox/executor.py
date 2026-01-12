from typing import List, Dict, Any
from datetime import datetime
from mnemosyne.core.schemas import ContentBrief, Creative
from .gemini_client import GeminiImageClient

class GeneratedAsset:
    def __init__(self, path: str, prompt: str, metadata: Dict[str, Any]):
        self.path = path
        self.prompt = prompt
        self.metadata = metadata

class ContentExecutor:
    """
    Execution Layer.
    Translates Mnemosyne Briefs -> Prompts -> Images.
    """
    def __init__(self):
        self.client = GeminiImageClient()

    def generate_assets(self, brief: ContentBrief) -> List[GeneratedAsset]:
        """
        Generates 5 assets based on the brief.
        """
        assets = []
        
        # 1. Translate Brief to Prompt
        # Logic: Combine Visual + Narrative + Risk Context
        base_prompt = (
            f"Visual Style: {brief.visual_intent}. "
            f"Subject: {brief.narrative_intent}. "
            f"Important Context: {brief.risk_notes}. "
            f"Compose for professional LinkedIn audience."
        )
        
        # 2. Generate 5 Variations (Simulated by generic prompt nuances if needed, or just 5 calls)
        # We will add slight variations to the prompt to force diversity if the model is static? 
        # Or just rely on seed variance. 
        # The task says "Convert it into natural-language image prompts". Plural.
        
        variations = [
            "Wide shot, establishment",
            "Close up, detail oriented",
            "Dynamic angle, action",
            "Minimalist composition",
            "Warm lighting, human connection"
        ]
        
        for i, var in enumerate(variations):
            prompt = f"{base_prompt} ({var})"
            print(f"  > Executing Prompt {i+1}: {prompt[:60]}...")
            
            path = self.client.generate_image(prompt)
            
            # 3. Traceability Metadata
            meta = {
                "brief_id": brief.id,
                "assumptions": brief.assumptions_referenced,
                "visual_intent": brief.visual_intent,
                "timestamp": datetime.utcnow().isoformat(),
                "generator": "Gemini (Auto-Model)"
            }
            
            assets.append(GeneratedAsset(path, prompt, meta))
            
        return assets
