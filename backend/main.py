from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
import time
import logging
import os

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("documind")

# Initialize FastAPI App
app = FastAPI(
    title="DocuMind AI API",
    description="Enterprise Document Intelligence & Agent Platform",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://docu-mind-swart.vercel.app",
        "http://localhost:8080",  # For local development
        "http://localhost:5173",  # Vite default port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        logger.info(f"Response: {response.status_code} | Time: {process_time:.2f}ms")
        return response
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error", "error": str(e)}
        )

# Standard init
from backend.routes import upload, query, auth, documents, notes
from backend.database.postgres import engine, Base

@app.get("/")
async def root():
    return {"message": "Welcome to DocuMind AI API", "status": "online"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    # Create tables in DB during startup, not import
    try:
        logger.info("Initializing database tables...")
        if engine:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables initialized successfully.")
        else:
            logger.error("Database engine not initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

    logger.info("Listing all registered routes:")
    for route in app.routes:
        methods = getattr(route, "methods", [])
        logger.info(f"Route: {route.path} | Methods: {methods}")

    port = os.getenv("PORT", "10000")
    logger.info(f"App is starting on port {port}...")

# Include Routes after startup logic is defined (though order doesn't strictly matter for events)
app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(query.router)
app.include_router(documents.router)
app.include_router(notes.router)
