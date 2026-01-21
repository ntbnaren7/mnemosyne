from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List

from src.monthly_production.agent import MonthlyProductionAgent
from src.monthly_production.schemas import CompanyContext, MonthPlan, CompanyStage, TonePreference
from sandbox.executor import ContentExecutor

router = APIRouter()

import json
import os

DB_PATH = "storage/prototype_db.json"

def load_db():
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_db(data):
    # Ensure storage dir exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=2, default=str)

# Load on startup
plan_store = load_db() 

class GenerateRequest(BaseModel):
    name: str
    industry: str
    description: str
    stage: CompanyStage
    tone: TonePreference
    target_audience: List[str]
    posting_frequency_per_week: int = 2

@router.post("/generate")
async def generate_plan(request: GenerateRequest):
    try:
        # 1. Initialize Agent
        agent = MonthlyProductionAgent()
        
        # 2. Create Context
        context = CompanyContext(**request.model_dump())
        
        # 3. Generate Plan (Planning Layer)
        plan = agent.generate_month_plan(context)
        
        # 4. Execute Sandbox (Execution Layer) - For 5 posts
        # In a real app this is async background task.
        executor = ContentExecutor()
        generated_assets = {}
        
        for post in plan.posts:
            print(f"Generating assets for {post.id}...")
            assets = executor.generate_assets(post)
            # Store just the path for the UI (Accessing the first variant)
            if assets:
                generated_assets[post.id] = assets[0].path
            
        # 5. Store Result
        plan_store["latest"] = {
            "plan": plan.model_dump(mode='json'), # Ensure serialization
            "assets": generated_assets
        }
        save_db(plan_store)
        
        return {"status": "success", "plan_id": "latest"}
    
    except Exception as e:
        print(f"Error generating plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/latest")
async def get_latest_plan():
    if "latest" not in plan_store:
        raise HTTPException(status_code=404, detail="No plan generated yet")
    return plan_store["latest"]

class EditRequest(BaseModel):
    post_id: str
    image_data: str # Base64
    change_description: str

@router.post("/edit/save")
async def save_edit(request: EditRequest):
    if "latest" not in plan_store:
        raise HTTPException(status_code=404, detail="No plan found")
    
    # 1. Decode and Save Image
    import base64
    import os
    
    try:
        # Remove header if present
        if "," in request.image_data:
            header, encoded = request.image_data.split(",", 1)
        else:
            encoded = request.image_data
            
        data = base64.b64decode(encoded)
        # Fix: Save to generated_assets directory
        basename = f"sandbox_output_EDIT_{request.post_id}.png"
        filename = os.path.join("generated_assets", basename)
        
        with open(filename, "wb") as f:
            f.write(data)
            
        # 2. Update Store (Store only basename for Frontend compatibility)
        plan_store["latest"]["assets"][request.post_id] = basename
        save_db(plan_store)
        
        # 3. Log Override (Traceability)
        # In a real system, we'd persist this to the MemoryManager's override log.
        print(f"[HUMAN_OVERRIDE] Post: {request.post_id} | Action: {request.change_description} | New Asset: {filename}")
        
        return {"status": "success", "new_asset": filename}
        
    except Exception as e:
        print(f"Error saving edit: {e}")
        raise HTTPException(status_code=500, detail=str(e))
