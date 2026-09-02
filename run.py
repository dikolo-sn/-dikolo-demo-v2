import os
from fastapi import FastAPI, Request, Form # Rajoute Form
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse # Rajoute RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware # Remet ça
from datetime import datetime

app = FastAPI(title="DiKoLo")

# REMET LE MIDDLEWARE
app.add_middleware(SessionMiddleware, secret_key="dikolo_secret_2026", same_site="lax", https_only=False)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

USERS_DB = {"demo@dikolo.com": {"password": "demo", "paye": False, "nom": "Demo"}}
DEMO_LIMITS = {"produits": 10, "ventes_jour": 3}
compteur_demo = {"produits": 0, "ventes": 0, "date": datetime.now().date()}

def get_user(request: Request):
    email = request.session.get("user") # Remet les sessions
    if not email: return None
    return USERS_DB.get(email)

@app.middleware("http")
async def restriction_middleware(request: Request, call_next):
    path = request.url.path
    if path.startswith("/login") or path.startswith("/static"): return await call_next(request) # Autorise /login
    user = get_user(request)
    if not user: return RedirectResponse("/login") # Redirige si pas connecté
    # ... le reste du code des limites reste pareil
    return await call_next(request)

# REMET CES 3 ROUTES
@app.get("/login", response_class=HTMLResponse)
def login_get(request: Request): return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login_post(request: Request, email: str = Form(...), password: str = Form(...)):
    user = USERS_DB.get(email)
    if user and user["password"] == password:
        request.session["user"] = email
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Email ou mot de passe incorrect"})

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    user = get_user(request)
    if not user: return RedirectResponse("/login") # Protège la page d'accueil
    return templates.TemplateResponse("index.html", {"request": request, "user": user, "paye": user["paye"]})
