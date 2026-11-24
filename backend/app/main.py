import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import PROJECT_NAME, ENV
from app.routes.career import router as career_router
from app.routes.students import router as students_router
from app.routes.progress import router as progress_router
from app.routes.gap_analyzer import router as gap_analyzer_router
from app.routes.ai import router as ai_router
from app.routes.recommender import router as recommender_router
from app.utils.firebase import init_firebase_app

# ── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("levelup")

# ── Rate Limiter ───────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])

# ── Lifespan ───────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_firebase_app()
    logger.info("Firebase initialized, %s is ready (%s)", PROJECT_NAME, ENV)
    yield
    logger.info("Shutting down %s", PROJECT_NAME)

app = FastAPI(
    title=PROJECT_NAME,
    description="LevelUP – AI-powered career path & learning roadmap agent",
    version="2.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter

# ── Rate limit error handler ──────────────────────────────────────────────
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."},
    )

# ── Global exception handler ─────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error on %s %s: %s", request.method, request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

# ── CORS ───────────────────────────────────────────────────────────────────
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "https://level-up-new.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request logging middleware ─────────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s %d %.0fms",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response

# ── Routes ─────────────────────────────────────────────────────────────────
app.include_router(career_router)
app.include_router(students_router)
app.include_router(progress_router)
app.include_router(gap_analyzer_router)
app.include_router(ai_router)
app.include_router(recommender_router)


@app.get("/")
def root():
    return {"app": PROJECT_NAME, "env": ENV, "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy"}
