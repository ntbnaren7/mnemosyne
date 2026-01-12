import os
from google import genai
from dotenv import load_dotenv

# Load API key
load_dotenv()

def test_direct_instantiation():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found.")
        return

    # Modern SDK Client
    client = genai.Client(api_key=api_key)
    print("API Key Configured (google-genai v1.0+).")

    try:
        print("Attempting to generate image using 'imagen-3'...")
        response = client.models.generate_images(
            model='imagen-3',
            prompt="A futuristic glowing blue cube on a dark background",
            config=dict(number_of_images=1)
        )
        
        print("Generation call complete.")
        if response.generated_images:
            print("SUCCESS: Image generated.")
            response.generated_images[0].image.save("debug_output.png")
            print("Saved to debug_output.png")
        else:
            print("FAILURE: No images returned.")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    test_direct_instantiation()
