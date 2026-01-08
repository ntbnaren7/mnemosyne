import uuid
from datetime import datetime
from ..core.schemas import VisualIntent, ImageArtifact
from ..core.interfaces import ImageRenderer

class MockStableDiffusionRenderer(ImageRenderer):
    """
    Simulates a text-to-image generator.
    Deterministic output for testing causal links.
    """
    async def render(self, intent: VisualIntent) -> ImageArtifact:
        # Simulate rendering latency/process
        
        # Create artifact
        artifact_id = f"img_{uuid.uuid4().hex[:8]}"
        
        # In a real system, this would call Stable Diffusion API
        # For V0.5, we return a mock artifact
        
        return ImageArtifact(
            artifact_id=artifact_id,
            visual_intent_used=intent,
            renderer_name="MockStableDiffusion_V0.5",
            file_path=f"storage/images/{artifact_id}.png",
            fidelity_notes="High fidelity mock",
            timestamp=datetime.utcnow()
        )
