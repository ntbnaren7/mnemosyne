from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import os

from src.web.routers.planning import plan_store
from sandbox.decomposer import ImageDecomposer

router = APIRouter()
decomposer = None

def get_decomposer():
    global decomposer
    if decomposer is None:
        decomposer = ImageDecomposer()
    return decomposer

@router.get("/decompose/{post_id}")
async def decompose_image(post_id: str):
    if "latest" not in plan_store or post_id not in plan_store["latest"]["assets"]:
        raise HTTPException(status_code=404, detail="Post or asset not found")
        
    asset_path = plan_store["latest"]["assets"][post_id]
    
    # Resolve path (Handle storage update)
    if not os.path.exists(asset_path):
        possible_path = os.path.join("generated_assets", asset_path)
        if os.path.exists(possible_path):
            asset_path = possible_path
    
    try:
        service = get_decomposer()
        # Decompose
        # Note: In production this should be async/background queue.
        # Here we run blocking for prototype simplicity (easyocr + cv2 is heavy)
        result = service.decompose(asset_path)
        
        return result.to_dict()
        
    except Exception as e:
        print(f"Error decomposing image: {e}")
        raise HTTPException(status_code=500, detail=str(e))
