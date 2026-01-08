from fastapi.testclient import TestClient
from web.backend.main import app
import os

client = TestClient(app)

def test_generate_images():
    print("--- MNEMOSYNE WEB POC: VERIFICATION ---")
    
    # 1. Test Static Landing Page
    response = client.get("/")
    assert response.status_code == 200
    print("[PASS] Serving Landing Page")
    
    # 2. Test Image Generation (Intelligent Mocking)
    payload = {
        "prompts": [
            "Our diverse team collaborating in open office", # Expect mock_office
            "AI server architecture",                    # Expect mock_tech
            "Strategic board meeting",                   # Expect mock_meeting
            "Global expansion city skyline",             # Expect mock_city
            "Productivity at home desk"                  # Expect mock_desk
        ]
    }
    
    response = client.post("/api/generate-images", json=payload)
    print(f"[DEBUG] Mock Response Status: {response.status_code}")
    if response.status_code != 200:
        print(f"[DEBUG] Response Content: {response.text}")
    
    try:
        data = response.json()
    except Exception as e:
        print(f"[ERROR] JSON Decode Failed: {e}")
        print(f"[DEBUG] Raw Response: {response.text}")
        raise e
        
    images = data["images"]
    
    print(f"[PASS] Mock Generation endpoint returned {len(images)} images")
    
    # 3. Test Real AI Fallback (Invalid Key)
    # The system should print an error but return results via fallback
    print("Testing Real AI Fallback...")
    payload_real = {
        "prompts": ["Future of AI"],
        "api_key": "INVALID_KEY_FOR_TESTING"
    }
    response = client.post("/api/generate-images", json=payload_real)
    assert response.status_code == 200
    data = response.json()
    assert len(data["images"]) == 1
    print("[PASS] Real AI Fallback handled gracefully (returned image)")

    print("\n--- VERIFICATION COMPLETE ---")

if __name__ == "__main__":
    test_generate_images()
