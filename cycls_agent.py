import cycls
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
import asyncio
from pathlib import Path

from app.services.ai_service import run_campaign
from app.services.memory import load_memory

os.getenv("OPENAI_API_KEY")

# Get the absolute path
# BASE_DIR = Path(__file__).resolve().parent
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

from app.services.ai_service import run_campaign
from app.services.memory import load_memory

@cycls.app(
    name="creative-campaign-agent",
    image={
        "pip": [
            "openai",
            "fastapi[standard]",
            "python-multipart",
            "jinja2"
        ],
        "copy": ["app"]
    } 
)
def create_fastapi_app():
    """Create and return your FastAPI app"""
    
    app = FastAPI()
    
    # Mount static files
    # static_dir = BASE_DIR / "static"
    static_dir = os.path.join(BASE_DIR, "static")
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    class CampaignRequest(BaseModel):
        product_name: str
        product_desc: str
        target_audience: str
        brand_voice: str = "Authentic, Refreshing"
        output_language: str = "English"

    @app.get("/", response_class=HTMLResponse)
    async def index():
        # template_path = BASE_DIR / "templates" / "index.html"
        template_path = os.path.join(BASE_DIR, "templates") + "/index.html"
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            return HTMLResponse(content=html_content)
        except FileNotFoundError:
            return HTMLResponse(content="<h1>Error: templates/index.html not found</h1>", status_code=404)

    @app.post("/generate")
    async def generate(req: CampaignRequest):
        
        async def event_stream():
            memory = load_memory()
            
            yield f"data: {json.dumps({'type': 'step', 'content': f'Loaded memory: {len(memory)} campaigns'})}\n\n"
            await asyncio.sleep(0.1)

            try:
                async for chunk in run_campaign(req):
                    yield f"data: {json.dumps(chunk)}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

            yield "data: [DONE]\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    return app

# For local development
# if __name__ == "__main__":
#     import uvicorn
#     app = create_fastapi_app()
#     print("🚀 Creative Campaign Agent starting locally...")
#     print("📍 Open http://127.0.0.1:8000 in your browser")
#     uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    import cycls
    import uvicorn
    app = create_fastapi_app()
    print("🚀 Creative Campaign Agent starting locally...")
    print("📍 Open http://127.0.0.1:8000 in your browser")
  
    uvicorn.run(app, host="127.0.0.1", port=8000)