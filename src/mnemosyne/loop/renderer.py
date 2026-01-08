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
        filename = f"{artifact_id}.png"
        output_dir = "storage_poc/images"
        import os
        os.makedirs(output_dir, exist_ok=True)
        file_path = f"{output_dir}/{filename}"
        
        # Generate a placeholder image using Pillow (part of streamit dependencies)
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Color based on intent for visual variety
            color_map = {
                "abstract": (200, 200, 255),
                "illustrative": (255, 200, 200)
            }
            bg_color = color_map.get(intent.visual_style, (240, 240, 240))
            
            img = Image.new('RGB', (512, 512), color=bg_color)
            d = ImageDraw.Draw(img)
            
            # Draw simplistic text/shapes
            d.text((20, 20), f"Style: {intent.visual_style}", fill=(0,0,0))
            d.text((20, 40), f"Comp: {intent.composition}", fill=(0,0,0))
            d.text((20, 60), f"Humans: {intent.human_presence}", fill=(0,0,0))
            
            # Simple shape for composition
            if intent.composition == "subject_centered":
                d.ellipse([150, 150, 362, 362], outline=(0,0,0), width=3)
            
            img.save(file_path)
            
        except ImportError:
            # Fallback if PIL fails
            with open(file_path, "w") as f:
                f.write("Placeholder Image")
        
        return ImageArtifact(
            artifact_id=artifact_id,
            visual_intent_used=intent,
            renderer_name="MockStableDiffusion_V0.5",
            file_path=file_path,
            fidelity_notes="Placeholder Grid",
            timestamp=datetime.utcnow()
        )
