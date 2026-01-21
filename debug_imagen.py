import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

def debug_gemini():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found.")
        return

    client = genai.Client(api_key=api_key)
    
    print("--- Listing Models ---")
    try:
        # Pager object, iterate
        for m in client.models.list():
            # Check if it supports image generation (heuristic matching)
            if "imagen" in m.name.lower():
                print(f"Found Image Model: {m.name} | Supported Methods: {m.supported_actions if hasattr(m, 'supported_actions') else 'Unknown'}")
            
    except Exception as e:
        print(f"Error listing models: {e}")

    print("\n--- Testing Generation ---")
    model_id = 'imagen-3.0-generate-001' 
    print(f"Attempting generation with: {model_id}")
    
    try:
        response = client.models.generate_images(
            model=model_id,
            prompt="A futuristic city",
            config=dict(number_of_images=1)
        )
        if response.generated_images:
            print("SUCCESS: Image generated.")
        else:
            print("FAILED: No images returned.")
    except Exception as e:
        print(f"FAILURE with {model_id}: {e}")

if __name__ == "__main__":
    debug_gemini()
