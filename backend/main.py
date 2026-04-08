from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
import time
import logging

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
    allow_origins=["*"],
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

# Create tables in DB
Base.metadata.create_all(bind=engine)

# Include Routes
app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(query.router)
app.include_router(documents.router)
app.include_router(notes.router)

@app.get("/")
async def root():
    return {"message": "Welcome to DocuMind AI API", "status": "online"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    logger.info("Listing all registered routes:")
    for route in app.routes:
        logger.info(f"Route: {route.path} | Methods: {route.methods}")
