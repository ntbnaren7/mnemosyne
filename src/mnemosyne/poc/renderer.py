import asyncio
import uuid
import os
from datetime import datetime
from typing import Optional

# Import Pillow (available in environment)
from PIL import Image, ImageDraw, ImageFont

from ..core.schemas import VisualIntent, ImageArtifact
from ..core.interfaces import ImageRenderer
from ..poc.render_presets import RenderPreset

class SmartRenderer:
    """
    CEO Demo Renderer.
    Combines pre-generated SD backgrounds with programmatic text overlay.
    """
    
    def __init__(self, assets_dir="src/mnemosyne/poc/assets"):
        self.assets_dir = assets_dir
        
    async def render(self, intent: VisualIntent, headline: str = "", preset: Optional[RenderPreset] = None) -> ImageArtifact:
        # Determine preset if not provided
        if not preset:
            preset = self._map_intent_to_preset(intent)
            
        # Select background asset
        bg_file = self._get_asset_filename(preset)
        bg_path = os.path.join(self.assets_dir, bg_file)
        
        # Create output artifact path
        artifact_id = f"img_{uuid.uuid4().hex[:8]}"
        filename = f"{artifact_id}.png"
        output_dir = "storage_poc/images"
        os.makedirs(output_dir, exist_ok=True)
        output_path = f"{output_dir}/{filename}"
        
        # Rendering Logic
        try:
            # Load Background
            if os.path.exists(bg_path):
                img = Image.open(bg_path).convert("RGB")
            else:
                # Fallback if asset missing (should not happen in controlled demo)
                img = Image.new('RGB', (1024, 1024), color=(240, 240, 240))
                
            # Resize to LinkedIn standard if needed (1024x1024 for demo)
            img = img.resize((1024, 1024))
            
            # Overlay Text
            if headline:
                d = ImageDraw.Draw(img)
                W, H = img.size
                
                # Draw Overlay Box (Professional Style)
                # Bottom third style
                overlay_h = 300
                shape = [(0, H - overlay_h), (W, H)]
                d.rectangle(shape, fill=(0, 0, 0, 200)) # Dark semi-transparent
                
                # Draw Text
                try:
                    # Windows specific or fallback
                    font = ImageFont.truetype("arial.ttf", 50)
                except IOError:
                    font = ImageFont.load_default()
                
                # Simple Text Wrap
                lines = []
                words = headline.split()
                current_line = []
                for word in words:
                    current_line.append(word)
                    if len(" ".join(current_line)) > 25: # Char limit per line
                        lines.append(" ".join(current_line[:-1]))
                        current_line = [word]
                lines.append(" ".join(current_line))
                
                # Draw lines
                y_text = H - overlay_h + 50
                for line in lines:
                   # Center text horizontally
                   # Approximation for centering without bbox precision on default font
                   d.text((50, y_text), line, font=font, fill=(255, 255, 255))
                   y_text += 70
                        
            img.save(output_path)
            
        except Exception as e:
            # Fallback
            with open(output_path, "w") as f:
                f.write(f"Error rendering: {e}")
        
        return ImageArtifact(
            artifact_id=artifact_id,
            visual_intent_used=intent,
            renderer_name="SmartRenderer_V1",
            file_path=output_path,
            fidelity_notes=f"Preset: {preset.name}",
            timestamp=datetime.utcnow()
        )

    def _map_intent_to_preset(self, intent: VisualIntent) -> RenderPreset:
        if intent.visual_style == "illustrative" or intent.human_presence == "explicit":
            return RenderPreset.ILLUSTRATED_HUMAN_CARD
        if intent.visual_style == "abstract":
            return RenderPreset.ABSTRACT_SYSTEM_DIAGRAM
        return RenderPreset.TEXT_LED_BRAND_CARD

    def _get_asset_filename(self, preset: RenderPreset) -> str:
        if preset == RenderPreset.TEXT_LED_BRAND_CARD:
            return "bg_brand.png"
        elif preset == RenderPreset.ABSTRACT_SYSTEM_DIAGRAM:
            return "bg_saas.png"
        elif preset == RenderPreset.ILLUSTRATED_HUMAN_CARD:
            return "bg_human.png"
        return "bg_brand.png"
