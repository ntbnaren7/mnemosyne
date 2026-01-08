from enum import Enum

class RenderPreset(str, Enum):
    TEXT_LED_BRAND_CARD = "text_led_brand_card"
    ABSTRACT_SYSTEM_DIAGRAM = "abstract_system_diagram"
    ILLUSTRATED_HUMAN_CARD = "illustrated_human_card"

def get_stable_diffusion_prompt(preset: RenderPreset) -> str:
    if preset == RenderPreset.TEXT_LED_BRAND_CARD:
        return "minimalist corporate background, soft lighting, professional blue and white gradient, high quality, 8k, no text"
    elif preset == RenderPreset.ABSTRACT_SYSTEM_DIAGRAM:
        return "abstract network diagram background, connecting nodes, tech visualization, clean lines, white background, isometric, no text"
    elif preset == RenderPreset.ILLUSTRATED_HUMAN_CARD:
        return "flat vector illustration of a professional person, neutral pose, office setting, minimal style, corporate colors, no text, no facial features"
    return "minimal background"
