from dotenv import load_dotenv
from fastapi import FastAPI

from app.api import auth, bm_parts, intercars, asg

load_dotenv()

app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(bm_parts.router)
app.include_router(intercars.router)
app.include_router(asg.router)


@app.get("/")
async def root():
    return {"message": "Check4Parts API adapter is running"}
