import os
from google import genai
from dotenv import load_dotenv

# Load API key
load_dotenv()

def debug_gemini_capabilities():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found.")
        return

    client = genai.Client(api_key=api_key)
    print("API Key Configured.")

    # Test 1: generate_images on Gemini 2.0 Flash
    print("\n[TEST 1] generate_images(model='gemini-2.0-flash-exp')") 
    try:
        response = client.models.generate_images(
            model='gemini-2.0-flash-exp',
            prompt="A blue cube",
            config=dict(number_of_images=1)
        )
        if response.generated_images:
            print("SUCCESS: generate_images worked on Gemini 2.0 Flash")
            response.generated_images[0].image.save("debug_gemini_img.png")
            return
    except Exception as e:
        print(f"FAILED: {e}")

    # Test 2: generate_content(contents='Generate an image...') on Gemini 2.0 Flash
    print("\n[TEST 2] generate_content(model='gemini-2.0-flash-exp', contents='Generate an image...')")
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents="Generate an image of a blue cube."
        )
        print("Response received.")
        # Check for image parts
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data or part.file_data: # Conceptual check for image
                     print("SUCCESS: Image data found in generate_content response")
                     # Note: extracting bytes from part.inline_data.data if present
                else:
                    print(f"Part type: {part}")
        else:
            print("No candidates returned.")
            
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    debug_gemini_capabilities()
