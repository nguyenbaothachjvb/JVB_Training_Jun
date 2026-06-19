from fastapi import FastAPI
from auth_api_demo.routers.health import router as health_router
from auth_api_demo.routers.users import router as users_router

app = FastAPI()

app.include_router(health_router)
app.include_router(users_router)