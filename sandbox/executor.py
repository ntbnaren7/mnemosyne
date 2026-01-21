from typing import List, Dict, Any
from datetime import datetime
from src.monthly_production.schemas import PostBrief
from .gemini_client import GeminiImageClient
from .prompt_compiler import PromptCompiler

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
        self.compiler = PromptCompiler()

    def generate_assets(self, brief: PostBrief) -> List[GeneratedAsset]:
        """
        Generates 1 asset based on the semantic brief (One per post for this prototype).
        """
        assets = []
        
        # 1. Translate Brief to Prompt (Invisible Step)
        prompt = self.compiler.compile(brief)
        
        # 2. Execution
        print(f"  > Executing Image Generation for Post {brief.id}...")
        path = self.client.generate_image(prompt)
        
        # 3. Traceability Metadata
        meta = {
            "brief_id": brief.id,
            "assumptions": [a.id for a in brief.governing_assumptions],
            "visual_direction": brief.visual_direction,
            "timestamp": datetime.utcnow().isoformat(),
            "generator": "Gemini (Auto-Model)"
        }
        
        assets.append(GeneratedAsset(path, prompt, meta))
            
        return assets
