from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api import auth, listas, tareas
from app.db.database import Base, engine

Base.metadata.create_all(bind=engine)

limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

app = FastAPI(
    title="Voice2Task API",
    description="Convierte notas de voz en tareas estructuradas con IA",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ── Errores de validación legibles ─────────────────────────────────────────────
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errores = exc.errors()
    if errores:
        mensaje = errores[0].get("msg", "Error de validación")
        mensaje = mensaje.replace("Value error, ", "")
        # Mensajes de Pydantic en inglés → español
        if "valid email" in mensaje.lower():
            mensaje = "El email no es válido"
        if "field required" in mensaje.lower():
            mensaje = "Faltan campos obligatorios"
        if "string should have at least" in mensaje.lower():
            mensaje = "La contraseña debe tener al menos 8 caracteres"
        return JSONResponse(status_code=422, content={"detail": mensaje})
    return JSONResponse(status_code=422, content={"detail": "Error de validación"})


# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080",
        "https://voice2task.aroca.dev",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


# ── Headers de seguridad ───────────────────────────────────────────────────────
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response


# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api")
app.include_router(tareas.router, prefix="/api")
app.include_router(listas.router, prefix="/api")


@app.get("/")
def root():
    return {"status": "ok", "proyecto": "Voice2Task"}