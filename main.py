import redis.asyncio as redis
import uvicorn
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware

from conf.config import settings
from routes import contacts, auth, users

app = FastAPI()

app.include_router(auth.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(users.router, prefix="/api")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():

    """
    The startup function is called when the application starts up and connects to Redis server defined in settings for rate limiting initialization.

    """
    r = await redis.Redis(host=settings.redis_host,
                          port=settings.redis_port,
                          db=0,
                          encoding="utf-8",
                          decode_responses=True)
    await FastAPILimiter.init(r)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6500)
