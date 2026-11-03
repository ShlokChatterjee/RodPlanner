from fastapi import FastAPI

from .routes import router

app = FastAPI(
    title="rodplanner",
    version="0.1.0",
    description="Automatic lightning rod placement from building plan images.",
)
app.include_router(router)
