from fastapi import FastAPI, HTTPException, Request, Depends

from auth import auth_router
from api import api_router

from middleware import RoleMiddleware


app = FastAPI()
app.add_middleware(RoleMiddleware)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(api_router, prefix="/api")
