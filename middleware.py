from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from database.models import UserRole
from typing import List, Dict
from tools import verify_token, CREDENTIAL_EXCEPTION
from celery_app.worker import _send_email

ROLE_ENDPOINT_RULES: Dict[UserRole, Dict[str, List[str]]] = {
    UserRole.ADMIN: {
        "tasks": ["GET", "POST", "PUT", "PATCH", "DELETE"],
        "users": ["GET", "POST", "PUT", "DELETE"],
    },
    UserRole.DEVELOPER: {"tasks": ["GET", "POST", "PUT", "PATCH"], "users": ["GET"]},
    UserRole.USER: {"tasks": ["GET", "PATCH"], "users": ["GET"]},
    UserRole.WATCHER: {"tasks": ["GET"], "users": ["GET"]},
}

EXCLUDED_PATHS = [
    "/auth/login",
    "/docs",
    "/openapi.json",
]


class RoleMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
        try:
            endpoint = request.url.path

            if any(endpoint.startswith(path) for path in EXCLUDED_PATHS):
                return await call_next(request)

            auth_header = request.headers.get("Authorization")
            if auth_header is None or not auth_header.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authorization header missing or invalid",
                )

            token = auth_header.split(" ")[1]

            try:
                user = verify_token(token)
            except HTTPException:
                raise CREDENTIAL_EXCEPTION

            parts = endpoint.split("/")
            if len(parts) > 2:
                resource = parts[2]
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid API endpoint",
                )

            method = request.method
            if resource not in ROLE_ENDPOINT_RULES.get(
                user.role, {}
            ) or method not in ROLE_ENDPOINT_RULES[user.role].get(resource, []):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to access this resource",
                )
            request.state.user = user.user_id
            response = await call_next(request)
            return response

        except HTTPException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
            )

        # except Exception as exc:
        #     return JSONResponse(
        #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #         content={"detail": "Internal Server Error"},
        #     )
