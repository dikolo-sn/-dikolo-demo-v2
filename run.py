import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime

app = FastAPI(title="DiKoLo")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

USERS_DB = {"demo@dikolo.com": {"password": "demo", "paye": False, "nom": "Demo"}}
DEMO_LIMITS = {"produits": 10, "ventes_jour": 3}
compteur_demo = {"produits": 0, "ventes": 0, "date": datetime.now().date()}

# ON FORCE LE USER DEMO DIRECT
def get_user(request: Request):
    return USERS_DB.get("demo@dikolo.com")

@app.middleware("http")
async def restriction_middleware(request: Request, call_next):
    path = request.url.path
    if path.startswith("/static"): return await call_next(request)
    
    user = get_user(request) # toujours demo
    if compteur_demo["date"] != datetime.now().date():
        compteur_demo["ventes"] = 0
        compteur_demo["date"] = datetime.now().date()
    if user["paye"] == False:
        if path == "/produits/nouveau" and request.method == "POST":
            if compteur_demo["produits"] >= DEMO_LIMITS["produits"]:
                return JSONResponse({"detail": "Limit 10 products reached."}, 403)
            compteur_demo["produits"] += 1
        if path == "/ventes/nouvelle" and request.method == "POST":
            if compteur_demo["ventes"] >= DEMO_LIMITS["ventes_jour"]:
                return JSONResponse({"detail": "Limit 3 sales/day reached."}, 403)
            compteur_demo["ventes"] += 1
    return await call_next(request)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    user = get_user(request)
    return templates.TemplateResponse("index.html", {"request": request, "user": user, "paye": user["paye"]})

# ON SUPPRIME LOGIN ET LOGOUT POUR L'INSTANT
