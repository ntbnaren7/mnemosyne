import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

def list_gemini_models():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set.")
        return

    client = genai.Client(api_key=api_key)
    
    print(">>> Listing Models via google-genai SDK...")
    try:
        # Pager object
        pager = client.models.list()
        
        print(f"{'MODEL ID':<40} | {'DISPLAY NAME':<30}")
        print("-" * 75)
        
        for model in pager:
            # Check capabilities if possible, but just listing ID is a good start
            print(f"{model.name:<40} | {model.display_name:<30}")
            
    except Exception as e:
        print(f"FAILED to list models: {e}")

if __name__ == "__main__":
    list_gemini_models()
