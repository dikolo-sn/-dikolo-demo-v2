import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from datetime import datetime
from starlette.middleware.sessions import SessionMiddleware

app.add_middleware(SessionMiddleware, secret_key="dikolo_secret_key_12345")
app = FastAPI(title="DiKoLo")
app.add_middleware(SessionMiddleware, secret_key="dikolo_secret_change_moi_2026")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

USERS_DB = {"demo@dikolo.com": {"password": "demo", "paye": False, "nom": "Demo"}}

DEMO_LIMITS = {"produits": 10, "ventes_jour": 3}
compteur_demo = {"produits": 0, "ventes": 0, "date": datetime.now().date()}

def get_user(request: Request):
    email = request.session.get("user")
    if not email: return None
    return USERS_DB.get(email)

@app.middleware("http")
async def restriction_middleware(request: Request, call_next):
    path = request.url.path
    if path in ["/login", "/static"]: return await call_next(request)
    user = get_user(request)
    if not user: return RedirectResponse("/login")
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

@app.get("/login", response_class=HTMLResponse)
def login_get(request: Request): return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login_post(request: Request, email: str = Form(...), password: str = Form(...)):
    user = USERS_DB.get(email)
    if user and user["password"] == password:
        request.session["user"] = email
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Wrong credentials"})

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    user = get_user(request)
    return templates.TemplateResponse("index.html", {"request": request, "user": user, "paye": user["paye"]})
