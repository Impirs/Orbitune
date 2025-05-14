from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.routers import auth, favorites, oauth, connected_services, playlists
from fastapi.openapi.utils import get_openapi
import os
import logging
import time

app = FastAPI(title="Orbitune API")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add a longer session expiry and a dedicated secret key
app.add_middleware(
    SessionMiddleware, 
    secret_key=os.getenv("SESSION_SECRET_KEY", "orbitune_development_secret_key"),
    max_age=86400 * 30  # 30 days
)

# Add logging middleware to track request time and errors
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logging.info(f"Request completed: {request.method} {request.url.path} - {response.status_code} in {process_time:.3f}s")
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logging.error(f"Request failed: {request.method} {request.url.path} in {process_time:.3f}s - Error: {str(e)}")
        raise

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(favorites.router, prefix="/favorites", tags=["Favorites"])
app.include_router(oauth.router)
app.include_router(connected_services.router)
app.include_router(playlists.router, prefix="/playlists", tags=["Playlists"])

@app.get("/", include_in_schema=False)
def root():
    return {
        "message": "Orbitune backend is alive",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "endpoints": [
            {"path": route.path, "methods": list(route.methods)}
            for route in app.routes if hasattr(route, 'path')
        ]
    }

@app.get("/openapi.json", include_in_schema=False)
def custom_openapi():
    return get_openapi(
        title=app.title,
        version="1.0.0",
        routes=app.routes
    )
