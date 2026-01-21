from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

load_dotenv()

# Setup
app = FastAPI(title="Mnemosyne Production Agent")

# Mount Static
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")

# Mount Sandbox Output (for serving generated images)
# In production, this would be an S3 bucket or similar.
app.mount("/sandbox_images", StaticFiles(directory="generated_assets"), name="sandbox_images")

# Templates
templates = Jinja2Templates(directory="src/web/templates")

# Routers
from src.web.routers import planning, editor
app.include_router(planning.router, prefix="/api/plan")
app.include_router(editor.router, prefix="/api/editor")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Landing: Company Setup"""
    return templates.TemplateResponse("setup.html", {"request": request})

@app.get("/plan", response_class=HTMLResponse)
async def view_plan(request: Request):
    """View generated monthly plan"""
    return templates.TemplateResponse("plan.html", {"request": request})

@app.get("/post/{post_id}", response_class=HTMLResponse)
async def post_detail(request: Request, post_id: str):
    """Detail view for a post"""
    return templates.TemplateResponse("post_detail.html", {"request": request, "post_id": post_id})

@app.get("/editor/{post_id}", response_class=HTMLResponse)
async def editor(request: Request, post_id: str):
    """Creative Editor"""
    return templates.TemplateResponse("editor.html", {"request": request, "post_id": post_id})
