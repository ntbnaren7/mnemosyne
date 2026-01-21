import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

def test_model(client, model_name):
    print(f"\n>>> Testing Model: {model_name}")
    try:
        response = client.models.generate_images(
            model=model_name,
            prompt="A futuristic robot painting a canvas, high quality",
            config=dict(number_of_images=1)
        )
        if response.generated_images:
            print("   -> SUCCESS: Image Generated.")
            # Verify file write permissions here? No, just API for now.
            filename = f"generated_assets/debug_{model_name.replace('-', '_')}.png"
            response.generated_images[0].image.save(filename)
            print(f"   -> Saved to {filename}")
        else:
            print("   -> SUCCESS (Response OK) but no images?")
    except Exception as e:
        print(f"   -> FAILED: {str(e)}")

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set.")
        return
        
    client = genai.Client(api_key=api_key)
    
    # List of candidates to try
    models = [
        "imagen-3.0-generate-001",
        "gemini-2.0-flash-exp",
        "imagen-4.0-fast-generate-001"
    ]
    
    for m in models:
        test_model(client, m)

if __name__ == "__main__":
    os.makedirs("generated_assets", exist_ok=True)
    main()
