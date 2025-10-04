from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

# Importa el backend
from app.scraper_api import app as scraper_app

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # limitar en prod
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir estáticos
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "frontend", "static")), name="static")

# Servir HTML
@app.get("/")
def serve_index():
    return FileResponse(os.path.join(BASE_DIR, "frontend", "static", "index.html"))

# ✅ Montar la API en /api (NO en /)
app.mount("/api", scraper_app)
