from typing import Any, Callable
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import Session, select
from starlette.middleware.base import BaseHTTPMiddleware
from src.auth.jwt_handler import verify_access_token
from src.database.config import get_settings
from src.database.database import get_session
from src.models.access_policy import AccessPolicy
from src.models.role import Role
from src.permission.access_control import AccessControl

from jose import jwt, exceptions
import re


class AccessControlMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        db: Session = next(get_session())
        try:
            # Bypass verification for service routes
            if request.url.path in [
                "/favicon.ico",
                "/docs",
                "/openapi.json",
                "/redoc",
                "/",
                "/static/styles.css",
                "/login",
                "/logout",
                "/register",
                "/error",
                "/api/oauth/signin",
                "/api/oauth/signup",
            ]:
                return await call_next(request)

            # 1️⃣ Сначала пытаемся получить токен из заголовка Authorization
            token = request.headers.get("Authorization")

            # 2️⃣ Если в заголовке нет, пробуем извлечь токен из cookie
            if not token:
                token = request.cookies.get("access_token")

            # 3️⃣ Если токен отсутствует, выбрасываем ошибку
            if token is None or not token.startswith("Bearer "):
                raise HTTPException(
                    status_code=401, detail="Authorization token missing"
                )

            # декодируем токен
            token = token[7:]
            payload = verify_access_token(
                token=token, secret_key=get_settings().SECRET_KEY
            )
            user_role = payload.get("user").get("role")

            # Даем полный доступ админу без проверок
            if user_role == "admin":
                return await call_next(request)

            # Проверяем доступ на основе AccessPolicy
            path = request.url.path
            method = request.method.lower()
            # Вырезаем UUID из строки
            uuid_pattern = re.compile(
                r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
            )
            id_pattern = re.compile(
                r"(\d+)"
            )
            clear_path = uuid_pattern.sub("%", path)
            clear_path = id_pattern.sub("%", clear_path)
            role_instance = db.query(Role).filter(Role.name == user_role).first()
            # SQLAlchemy/SQLModel style query using LIKE correctly
            statement = select(AccessPolicy).where(
                AccessPolicy.role == role_instance,
                AccessPolicy.resource.like(clear_path),  # Correct usage of LIKE
                AccessPolicy.action == method.upper()
            )

            policy = db.exec(statement).all()

            if not policy:
                raise HTTPException(status_code=403, detail="Forbidden")

            return await call_next(request)

        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={"detail": e.detail})

        except exceptions.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")

        except exceptions.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
