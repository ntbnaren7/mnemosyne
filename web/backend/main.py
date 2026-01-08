from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import random
import os
try:
    from .real_generator import RealGenerator, ASSET_MAP
except ImportError:
    from real_generator import RealGenerator, ASSET_MAP

app = FastAPI()

class GenerateRequest(BaseModel):
    prompts: List[str]
    api_key: Optional[str] = None

@app.post("/api/generate-images")
async def generate_images(request: GenerateRequest):
    """
    Hybrid Generation Endpoint.
    If api_key provided: Uses RealGenerator (Gemini) for "Designed Posters".
    If no key: Uses pure Mock Logic.
    """
    if len(request.prompts) > 5:
        raise HTTPException(status_code=400, detail="Max 5 prompts allowed")

    results = []
    
    # --- REAL AI MODE ---
    if request.api_key:
        try:
            generator = RealGenerator(api_key=request.api_key)
            for prompt in request.prompts:
                # Call Real Logic
                image_url = generator.generate_poster(prompt)
                results.append(image_url)
            return {"images": results}
        except Exception as e:
            print(f"Real Gen Failed: {e}. Falling back to mock.")
            # Fall through to mock if init fails
    
    # --- MOCK MODE (Fallback) ---
    available_assets = list(ASSET_MAP.keys())
    
    for prompt in request.prompts:
        prompt_lower = prompt.lower()
        selected_asset = "mock_office.png" # Default
        
        # Keyword matching
        best_match_score = 0
        for asset, keywords in ASSET_MAP.items():
            score = sum(1 for k in keywords if k in prompt_lower)
            if score > best_match_score:
                best_match_score = score
                selected_asset = asset
        
        if best_match_score == 0:
             selected_asset = random.choice(available_assets)

        results.append(f"/assets/{selected_asset}")

    return {"images": results}

# Serve Assets
app.mount("/assets", StaticFiles(directory="web/assets"), name="assets")

# Serve Frontend
app.mount("/", StaticFiles(directory="web/static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
