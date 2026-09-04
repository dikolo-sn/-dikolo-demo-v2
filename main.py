from fastapi import FastAPI, Request, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import datetime, timedelta

app = FastAPI()

# ===== CONFIG SECURITE =====
DATE_EXPIRATION = datetime(2026, 10, 3)   # 30 jours de test
USER = "admin"
PASS = "1234"

CSS = """<style>
body{font-family:Arial;margin:0;background:#f4f6f9}
header{background:#1e3a8a;color:white;padding:15px}
.nav-links{display:flex;gap:15px;flex-wrap:wrap}
.nav-links a{color:white;text-decoration:none}
.login-box{width:300px;margin:100px auto;padding:20px;background:white;border-radius:10px;box-shadow:0 0 10px #ccc}
input,button{width:100%;padding:10px;margin:5px 0}
button{background:#1e3a8a;color:white;border:none;cursor:pointer}
@media(max-width: 768px){.nav-links{flex-direction: column;}.login-box{width:90%}}
</style>"""

def build_menu(active):
    return f"<header><h2>DiKoLo v1.0 SECURISE</h2><nav class='nav-links'><a href='/dashboard'>Dashboard</a><a href='/produits'>Produits</a><a href='/logout'>Deconnexion</a></nav></header>"

# ===== MIDDLEWARE EXPIRATION =====
@app.middleware("http")
async def check_license(request: Request, call_next):
    if datetime.now() > DATE_EXPIRATION:
        return HTMLResponse("<h1 style='text-align:center;margin-top:100px'>Version d'essai expirée</h1>")
    return await call_next(request)

# ===== ROUTES LOGIN =====
@app.get("/login", response_class=HTMLResponse)
async def login_page():
    return HTMLResponse(f"{CSS}<div class='login-box'><h1>DiKoLo Login</h1><form method='post'><input name='username' placeholder='Username' required><input name='password' type='password' placeholder='Password' required><button type='submit'>Se connecter</button></form></div>")

@app.post("/login")
async def do_login(username: str = Form(...), password: str = Form(...)):
    if username == USER and password == PASS:
        response = RedirectResponse(url="/dashboard", status_code=302) # <- IMPORTANT
        response.set_cookie("user", "admin")
        return response
    return RedirectResponse(url="/login", status_code=302)

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie("user")
    return response

# ===== ROUTES APP =====
@app.get("/dashboard", response_class=HTMLResponse) # <- IMPORTANT
async def dashboard(user: str = Cookie(None)):
    if user != "admin": return RedirectResponse(url="/login")
    menu = build_menu("dashboard")
    return HTMLResponse(f"{CSS}{menu}
    <div class="welcome-box">
    <h1>Bienvenue admin</h1>
    <p>Version securisee + Mobile OK</p>
</div>
@app.get("/", response_class=HTMLResponse)
async def root():
    return RedirectResponse(url="/login")
