import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

def brute_force_discovery():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("No API Key.")
        return

    client = genai.Client(api_key=api_key)
    
    # 1. Hardcoded candidates to try
    candidates = [
        'imagen-3.0-generate-001',
        'imagen-2.0-generate-001',
        'imagen-3', 
        'gemini-1.5-pro',
        'gemini-1.5-flash',
        'gemini-2.0-flash-exp'
    ]
    
    # 2. Add listed models
    try:
        listed = [m.name for m in client.models.list()]
        print(f"Listed Models: {listed}")
        candidates.extend(listed)
    except Exception as e:
        print(f"List failed: {e}")

    # Deduplicate
    candidates = list(set(candidates))
    
    print(f"Testing {len(candidates)} models for generate_images capability...")
    
    for model_name in candidates:
        # Strip 'models/' prefix if present for clean testing, though SDK usually handles both
        clean_name = model_name.replace('models/', '')
        print(f"Testing: {clean_name}")
        try:
            response = client.models.generate_images(
                model=clean_name,
                prompt="A small red dot",
                config=dict(number_of_images=1)
            )
            if response.generated_images:
                print(f"!!! SUCCESS !!! Model '{clean_name}' generated an image!")
                return
        except Exception as e:
            # We expect 404 or 400 or AttributeError
            error_msg = str(e)
            if "NOT_FOUND" in error_msg:
                pass # Expected for invalid models
            elif "not supported" in error_msg.lower():
                pass
            else:
                 print(f"  Failed ({clean_name}): {error_msg[:100]}...")

    print("All models failed.")

if __name__ == "__main__":
    brute_force_discovery()
