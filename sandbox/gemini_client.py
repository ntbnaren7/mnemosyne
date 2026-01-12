import os
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
            return f"[MOCK IMAGE] Generated for: '{prompt[:30]}...'"
        
        try:
            # CORRECT PATTERN: Use the specific endpoint for Image Generation.
            # Discovered via brute-force: 'imagen-4.0-generate-001' works for this environment.
            response = self.client.models.generate_images(
                model='imagen-4.0-generate-001',
                prompt=prompt,
                config=dict(number_of_images=1)
            )
            
            if response.generated_images:
                image = response.generated_images[0]
                filename = f"sandbox_output_{abs(hash(prompt))}.png"
                image.image.save(filename)
                return filename
            else:
                 return "[ERROR] No images returned from Gemini."

        except Exception as e:
            # Graceful error handling for the UI
            return f"[ERROR] Generation failed: {str(e)}"
