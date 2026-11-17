import time
from datetime import datetime
from collections import defaultdict
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from .config import settings
from .db import engine, Base
from .routers import (
    auth,
    public,
    ai,
    grievances,
    status as status_router,
    cmo,
    officer,
)
from .seed import seed_database

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CM Kerala Public Grievance Redressal Portal API",
    version="1.0.0",
    description="Recruitment Prototype: Public Grievance Redressal Portal. Not affiliated with the Government of Kerala. All data fictional.",
    docs_url="/docs",
    redoc_url="/redoc",
)

# In-memory Rate Limiter
# Tracks requests per IP: { (ip, endpoint): [timestamps] }
_RATE_LIMIT_BUCKET = defaultdict(list)
RATE_LIMIT_RULES = {
    "/api/auth/login": (15, 60),      # 15 requests per 60 seconds
    "/api/contact": (10, 60),         # 10 requests per 60 seconds
    "/api/ai/analyze": (30, 60),       # 30 requests per 60 seconds
}

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "127.0.0.1"
    path = request.url.path

    if path in RATE_LIMIT_RULES:
        max_requests, window_seconds = RATE_LIMIT_RULES[path]
        now = time.time()
        bucket_key = f"{client_ip}:{path}"
        timestamps = _RATE_LIMIT_BUCKET[bucket_key]

        # Evict outdated timestamps
        _RATE_LIMIT_BUCKET[bucket_key] = [t for t in timestamps if now - t < window_seconds]
        if len(_RATE_LIMIT_BUCKET[bucket_key]) >= max_requests:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": f"Rate limit exceeded. Try again in a few seconds.",
                    "code": "RATE_LIMIT_EXCEEDED",
                },
            )
        _RATE_LIMIT_BUCKET[bucket_key].append(now)

    response = await call_next(request)
    return response


# Consistent Error Shape Handlers: { "detail": "...", "code": "..." }
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    code = getattr(exc, "code", None)
    if not code:
        if exc.status_code == 401:
            code = "UNAUTHORIZED"
        elif exc.status_code == 403:
            code = "FORBIDDEN"
        elif exc.status_code == 404:
            code = "NOT_FOUND"
        elif exc.status_code == 409:
            code = "CONFLICT"
        elif exc.status_code == 422:
            code = "VALIDATION_ERROR"
        else:
            code = "HTTP_ERROR"

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail), "code": code},
        headers=getattr(exc, "headers", None),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    first_error = errors[0]["msg"] if errors else "Invalid request data"
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": f"Validation error: {first_error}",
            "code": "VALIDATION_ERROR",
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected server error occurred. Please try again later.",
            "code": "INTERNAL_SERVER_ERROR",
        },
    )


# CORS Configuration
origins = [o.strip() for o in settings.FRONTEND_ORIGIN.split(",") if o.strip()]
if not origins or "*" in origins:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True if "*" not in origins else False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health Check (for uptime pings, cold starts, and waking up banner)
@app.get("/api/health")
def health_check():
    """Uptime and readiness ping for Render and cold-start monitor."""
    return {
        "status": "ok",
        "service": "CM Kerala Public Grievance Portal API",
        "timestamp": datetime.utcnow().isoformat(),
        "env": settings.ENV,
    }


# Include Routers with /api prefix
app.include_router(auth.router, prefix="/api")
app.include_router(public.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(grievances.router, prefix="/api")
app.include_router(status_router.router, prefix="/api")
app.include_router(cmo.router, prefix="/api")
app.include_router(officer.router, prefix="/api")


@app.on_event("startup")
def on_startup():
    """Ensure seeded demo data exists on launch."""
    try:
        seed_database()
    except Exception as e:
        print(f"Startup database check: {e}")
