import google.generativeai as genai
import os
import uuid
import random
import json
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Tuple, List

# Re-use the asset map for intelligent fallback
ASSET_MAP = {
    "mock_office.png": ["office", "team", "collaboration", "meeting", "people", "workplace", "diverse", "discussion"],
    "mock_tech.png": ["tech", "technology", "server", "data", "ai", "cyber", "code", "digital", "network", "future"],
    "mock_meeting.png": ["meeting", "boardroom", "strategy", "executive", "planning", "presentation", "corporate"],
    "mock_city.png": ["city", "skyline", "urban", "global", "business", "scale", "building", "architecture", "growth"],
    "mock_desk.png": ["desk", "remote", "home office", "laptop", "creative", "minimal", "focus", "work", "productivity"]
}

class RealGenerator:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.assets_dir = "web/assets"
        self.output_dir = "web/assets/generated"
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_poster(self, user_prompt: str) -> str:
        """
        Orchestrates the creation of a 'Designed Poster'.
        1. Uses Gemini to analyze intent and generate a headline.
        2. Selects the BEST background asset (intelligent mapping).
        3. Renders the poster with PIL.
        """
        try:
            # Step 1: Text Intelligence
            headline, visual_keywords = self._analyze_prompt_with_gemini(user_prompt)
            print(f"[RealGenerator] Prompt: '{user_prompt}' -> Headline: '{headline}' | Visuals: {visual_keywords}")

            # Step 2: Visual Selection (Intelligent Fallback)
            # We use the AI-generated visual description to find the best match
            bg_filename = self._select_best_asset(visual_keywords)
            bg_path = os.path.join(self.assets_dir, bg_filename)

            # Step 3: Render
            output_filename = f"gen_{uuid.uuid4().hex[:8]}.png"
            output_path = os.path.join(self.output_dir, output_filename)
            
            self._render_poster(bg_path, headline, output_path)
            
            return f"/assets/generated/{output_filename}"

        except Exception as e:
            print(f"[RealGenerator] Error: {e}")
            # Graceful failure fallback
            return f"/assets/mock_office.png"

    def _analyze_prompt_with_gemini(self, prompt: str) -> Tuple[str, str]:
        """
        Asks Gemini to act as a Creative Director.
        Returns: (Professional Headline, Visual Keywords)
        """
        sys_prompt = """
        You are a LinkedIn Content Strategist. 
        Analyze the user's topic and generate:
        1. A punchy, professional headline (max 8 words).
        2. A list of visual keywords to describe the ideal image.
        
        Output JSON only: {"headline": "...", "keywords": "..."}
        """
        
        try:
            response = self.model.generate_content(f"{sys_prompt}\nUser Topic: {prompt}")
            text = response.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(text)
            return data.get("headline", prompt), data.get("keywords", "corporate")
        except Exception as e:
            # LOG THE ERROR for debugging
            print(f"[RealGenerator] Gemini API Error: {e}")
            # Fallback to a safe, short headline if API fails
            return "Strategic Update", "corporate"

    def _select_best_asset(self, visual_keywords: str) -> str:
        """
        Matches generated keywords against asset tags.
        """
        kw_lower = visual_keywords.lower()
        best_asset = "mock_office.png"
        max_score = -1
        
        for asset, tags in ASSET_MAP.items():
            score = 0
            for tag in tags:
                if tag in kw_lower:
                    score += 1
            
            if score > max_score:
                max_score = score
                best_asset = asset
                
        # Randomize slightly if no strong match to avoid repetition
        if max_score == 0:
            return random.choice(list(ASSET_MAP.keys()))
            
        return best_asset

    def _render_poster(self, bg_path: str, headline: str, output_path: str):
        """
        Overlays text using PIL (Professional Style).
        """
        try:
            img = Image.open(bg_path).convert("RGB")
            # Ensure standard size
            img = img.resize((1024, 1024))
            draw = ImageDraw.Draw(img)
            W, H = img.size
            
            # --- STYLE: Modern Gradient Overlay ---
            # Create a localized dark gradient at the bottom for text readability
            # (Simulated by drawing multiple semi-transparent rectangles)
            overlay_height = 400
            for y in range(H - overlay_height, H):
                alpha = int(255 * ((y - (H - overlay_height)) / overlay_height) * 0.9)
                draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))

            # --- TYPOGRAPHY ---
            # Try to load a nice font, fallback to default
            try:
                # Arial Bold usually available on Windows
                font_path = "arialbd.ttf" 
                font_size = 60
                font = ImageFont.truetype(font_path, font_size)
            except:
                font = ImageFont.load_default()
                font_size = 40 # Mock size

            # Wrap Text
            lines = []
            words = headline.split()
            current_line = []
            
            # Rough char limit based on font size. 
            # 1024px width / ~30px per char (estimate for 60pt) = ~34 chars
            max_chars = 25 
            
            for word in words:
                current_line.append(word)
                if len(" ".join(current_line)) > max_chars:
                    lines.append(" ".join(current_line[:-1]))
                    current_line = [word]
            lines.append(" ".join(current_line))
            
            # Draw Text
            # Bottom-Left alignment with padding
            padding_x = 60
            padding_y_bottom = 120
            
            text_block_height = len(lines) * (font_size + 10)
            y_cursor = H - padding_y_bottom - text_block_height
            
            for line in lines:
                # Drop shadow for extra pop
                draw.text((padding_x + 2, y_cursor + 2), line, font=font, fill=(0, 0, 0))
                draw.text((padding_x, y_cursor), line, font=font, fill=(255, 255, 255))
                y_cursor += font_size + 15
                
            # Add subtle "branding" line
            draw.line([(padding_x, y_cursor + 20), (padding_x + 100, y_cursor + 20)], fill=(59, 130, 246), width=6)

            img.save(output_path)
            
        except Exception as e:
            print(f"Render failed: {e}")
            img.save(output_path) # Save original on fail
