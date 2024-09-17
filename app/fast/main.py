import uvicorn
from fastapi import FastAPI

from app.fast.routers import routers

app = FastAPI()

[app.include_router(router) for router in routers]


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
