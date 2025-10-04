from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ✅ Sirve los estáticos
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "frontend", "static")), name="static")

# ✅ Sirve el HTML principal
@app.get("/")
def serve_index():
    return FileResponse(os.path.join(BASE_DIR, "frontend", "static", "index.html"))
