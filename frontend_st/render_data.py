import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import Response, FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = Path(__file__).parent / "app_data.json"
HTML_FILE = Path(__file__).parent / "general_dashboard.html"


@app.get("/api/chats")
def get_static_data():
    print(DATA_FILE)
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))
@app.get("/")
def serve_general_frontend():
    return FileResponse(HTML_FILE, media_type="text/html")