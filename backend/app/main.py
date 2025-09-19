from dotenv import load_dotenv
from fastapi import FastAPI

from app.api import PROVIDER_REGISTRY, auth

load_dotenv()

app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

for _, router in PROVIDER_REGISTRY.items():
    app.include_router(router)


@app.get("/")
async def root():
    return {"message": "Check4Parts API adapter is running"}
