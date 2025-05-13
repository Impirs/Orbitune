from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.routers import auth, favorites, oauth, connected_services, playlists
from fastapi.openapi.utils import get_openapi
import os
import logging

app = FastAPI(title="Orbitune API")

logging.basicConfig(level=logging.INFO)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY", "dev_secret"))

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
