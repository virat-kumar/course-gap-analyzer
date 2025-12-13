"""FastAPI main application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes_pdf, routes_search, routes_analyze, routes_chat
from app.db.session import init_db

app = FastAPI(
    title="Syllabus Gap Analyzer API",
    description="API for comparing syllabus PDFs against industry job descriptions",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(routes_pdf.router)
app.include_router(routes_search.router)
app.include_router(routes_analyze.router)
app.include_router(routes_chat.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Syllabus Gap Analyzer API",
        "version": "1.0.0",
        "endpoints": {
            "pdf": "/pdf",
            "search": "/search",
            "analyze": "/analyze",
            "chat": "/chat"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


