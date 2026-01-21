import os
import random
from PIL import Image, ImageDraw, ImageFont
from google import genai
from typing import Optional

class GeminiImageClient:
    """
    Disposable client for Image Generation using google-genai SDK (v1.0+).
    CONSTRAINT: Uses standard model 'imagen-3.0-generate-001' as the endpoint.
    """
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("WARNING: GEMINI_API_KEY not found. Sandbox will mock generation.")
            self.mock_mode = True
            self.client = None
        else:
            self.client = genai.Client(api_key=api_key)
            self.mock_mode = False

    def generate_image(self, prompt: str) -> str:
        """
        Generates an image from a prompt.
        Returns: Path to saved image (simulated or real).
        """
        if self.mock_mode:
            return self._generate_mock_placeholder(prompt)
        
        try:
            # CORRECT PATTERN: Use the specific endpoint for Image Generation.
            # 3.0 is missing. 4.0-fast hit quota. Trying 4.0-standard.
            response = self.client.models.generate_images(
                model='imagen-4.0-generate-001',
                prompt=prompt,
                config=dict(number_of_images=1)
            )
            
            if response.generated_images:
                image = response.generated_images[0]
                # Save to generated_assets directory
                filename = os.path.join("generated_assets", f"sandbox_output_{abs(hash(prompt))}.png")
                image.image.save(filename)
                # Return basename for URL construction if needed, or relative path?
                # The app serves /sandbox_images/ -> generated_assets/
                # So if we return "sandbox_output_....png", the frontend needs /sandbox_images/sandbox_output...
                # If we return "generated_assets/sandbox_output...", frontend might break.
                # Let's return the relative path for internal logic, and ensure frontend handles it.
                # Actually, currently it returns "sandbox_output_X.png".
                # The frontend likely uses `/sandbox_images/{filename}`.
                # So we should return the BASENAME only, but save to the SUBDIR.
                return os.path.basename(filename)
            else:
                 print("[ERROR] No images returned from Gemini. Falling back to mock.")
                 return self._generate_mock_placeholder(prompt)

        except Exception as e:
            # Graceful error handling - return a placeholder instead of crashing or text
            print(f"[ERROR] Generation failed: {str(e)}")
            return self._generate_mock_placeholder(prompt)

    def _generate_mock_placeholder(self, prompt: str) -> str:
        """Helper to create a real image file for the UI to display during errors/mocking."""
        try:
            filename = os.path.join("generated_assets", f"sandbox_output_MOCK_{abs(hash(prompt))}.png")
            
            # Create a simple image
            img = Image.new('RGB', (800, 600), color=(30, 30, 35))
            d = ImageDraw.Draw(img)
            
            # Add text
            d.text((50, 250), "Gemini Generation Failed/Mocked", fill=(200, 200, 200))
            d.text((50, 300), f"Prompt: {prompt[:40]}...", fill=(150, 150, 150))
            d.text((50, 350), "(Check Server Logs)", fill=(150, 150, 150))
            
            img.save(filename)
            return os.path.basename(filename)
        except Exception as e:
            print(f"Failed to generate mock image: {e}")
            return "sandbox_output_FALLBACK.png" # Last resort
