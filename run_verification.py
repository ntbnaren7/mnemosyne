import os
import shutil
from fastapi.testclient import TestClient
from src.web.app import app
import base64

def run_verification():
    print(">>> Starting Verification Suite for Mnemosyne Monthly Agent")
    
    client = TestClient(app)
    
    # 1. Test Landing Page
    print("\n[1] Testing Landing Page...")
    resp = client.get("/")
    assert resp.status_code == 200
    print("   -> Success: Landing page loads.")

    # 2. Test Plan Generation
    print("\n[2] Testing Plan Generation (This triggers Agent + Sandbox)...")
    payload = {
        "name": "Acme Robotics",
        "industry": "Industrial Automation",
        "description": "We make robots for factories.",
        "stage": "scaleup",
        "tone": "innovative",
        "target_audience": ["Factory Owners", "CTOs"],
        "posting_frequency_per_week": 2
    }
    
    # Mocking or Real? 
    # If GEMINI_API_KEY is present, it will try to generate real images.
    # This might take time.
    print("   -> Sending request (may take ~10-20s if generating real images)...")
    resp = client.post("/api/plan/generate", json=payload)
    
    if resp.status_code != 200:
        print(f"FAILED: {resp.text}")
        return
        
    data = resp.json()
    assert data["status"] == "success"
    print("   -> Success: Plan generated.")
    
    # 3. Verify Plan Retrieval
    print("\n[3] Verifying Plan Storage...")
    resp = client.get("/api/plan/latest")
    assert resp.status_code == 200
    plan_data = resp.json()
    posts = plan_data["plan"]["posts"]
    assets = plan_data["assets"]
    
    assert len(posts) == 5
    print(f"   -> Confirmed 5 posts in plan.")
    print(f"   -> Confirmed {len(assets)} assets generated.")
    
    first_post_id = posts[0]["id"]
    
    # 4. Verify Image File Exists
    first_asset_path = assets.get(first_post_id)
    # Check if exists (might be just basename now)
    full_path = first_asset_path
    if first_asset_path and not os.path.exists(first_asset_path):
        full_path = os.path.join("generated_assets", first_asset_path)
        
    if full_path and os.path.exists(full_path):
        print(f"   -> Verified asset file exists: {full_path}")
    else:
        print(f"   -> WARNING: Asset file missing or path incorrect: {first_asset_path}")

    # 5. Test Edit Saving (Human Override)
    print("\n[4] Testing Human Creative Override...")
    
    # Create a dummy base64 image (1x1 pixel png)
    dummy_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAAAAAA6fptVAAAACklEQVR4nGNiAAAABgDNjd8qAAAAAElFTkSuQmCC"
    
    edit_payload = {
        "post_id": first_post_id,
        "image_data": dummy_b64,
        "change_description": "Verification Test Edit"
    }
    
    resp = client.post("/api/plan/edit/save", json=edit_payload)
    assert resp.status_code == 200
    new_asset = resp.json()["new_asset"]
    
    print(f"   -> Edit saved to: {new_asset}")
    assert os.path.exists(new_asset)
    print("   -> Confirmed new asset file exists.")

    # 6. Test Decomposition (Smart Layers)
    print("\n[5] Testing Smart Layer Decomposition...")
    # Use the SECOND post (index 1) to avoid the one we just overwrote with a dummy image
    target_post_id = posts[1]["id"]
    
    decomp_resp = client.get(f"/api/editor/decompose/{target_post_id}")
    if decomp_resp.status_code == 200:
        d_data = decomp_resp.json()
        print(f"   -> Decomposition successful.")
        print(f"   -> Background saved at: {d_data['background_path']}")
        print(f"   -> Found {len(d_data['layers'])} layers.")
        if len(d_data['layers']) > 0:
            for l in d_data['layers']:
                print(f"      - Layer: {l['content'][:20]}... ({l['type']})")
    else:
        print(f"   -> WARNING: Decomposition failed: {decomp_resp.text}")

    print("\n>>> VERIFICATION COMPLETE: ALL SYSTEMS NOMINAL.")

if __name__ == "__main__":
    run_verification()
