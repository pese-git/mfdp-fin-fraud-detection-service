import re
from typing import Any, Callable

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from jose import exceptions
from sqlmodel import Session, select
from src.auth.jwt_handler import verify_access_token
from src.database.config import get_settings
from src.database.database import get_session
from src.models.access_policy import AccessPolicy
from src.models.role import Role
from src.services.logging.logging import get_logger
from starlette.middleware.base import BaseHTTPMiddleware

logger = get_logger(logger_name="permission.access_control_middleware")


class AccessControlMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Any:
        db: Session = next(get_session())
        try:
            # Bypass verification for service routes
            if request.url.path in [
                "/favicon.ico",
                "/docs",
                "/openapi.json",
                "/redoc",
                "/",
                "/static/bootstrap/css/bootstrap.min.css",
                "/static/styles.css",
                "/login",
                "/logout",
                "/register",
                "/error",
                "/api/oauth/signin",
                "/api/oauth/signup",
                "/api/predict/send_task_result",
            ]:
                logger.debug("Маршрут '%s' не требует проверки доступа.", request.url.path)
                return await call_next(request)

            # Пытаемся получить токен из заголовка Authorization
            token = request.headers.get("Authorization")
            # Если в заголовке нет, пробуем извлечь из cookie
            if not token:
                token = request.cookies.get("access_token")

            # Если токен не найден или не начинается с "Bearer ", выбрасываем ошибку
            if token is None or not token.startswith("Bearer "):
                logger.warning("Не передан токен авторизации для %s", request.url.path)
                raise HTTPException(status_code=401, detail="Authorization token missing")

            # Удаляем "Bearer " из токена
            token = token[7:]
            logger.debug("Попытка верификации access_token для запроса %s", request.url.path)
            # Проверяем валидность токена и получаем payload пользователя
            secret_key = get_settings().SECRET_KEY
            if secret_key is None:
                raise RuntimeError("SECRET_KEY is not set in settings!")
            payload = verify_access_token(token=token, secret_key=secret_key)
            user = payload.get("user") or {}
            user_role = user.get("role")
            user_email = user.get("email", "unknown")

            logger.info(
                "Пользователь '%s' с ролью '%s' обращается к %s (%s)",
                user_email,
                user_role,
                request.url.path,
                request.method,
            )

            # Если пользователь - админ, предоставляем полный доступ без дальнейших проверок
            if user_role == "admin":
                logger.debug("Пользователь с ролью admin получил полный доступ.")
                return await call_next(request)

            # Проверка доступа для остальных ролей
            path = request.url.path
            method = request.method.lower()
            # Вырезаем UUID и числовые id для сравнения маршрутов с политиками доступа
            uuid_pattern = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")
            id_pattern = re.compile(r"(\d+)")
            clear_path = uuid_pattern.sub("%", path)
            clear_path = id_pattern.sub("%", clear_path)
            role_instance = db.query(Role).filter(Role.name == user_role).first()

            # Формируем SQL-запрос на доступ по ролям и экшенам
            statement = select(AccessPolicy).where(
                AccessPolicy.role == role_instance,
                AccessPolicy.resource.like(clear_path),  # type: ignore
                AccessPolicy.action == method.upper(),
            )
            policy = db.exec(statement).all()

            # Если политика не найдена, запрещаем доступ
            if not policy:
                logger.warning(
                    "Доступ запрещён для пользователя '%s' (%s) к ресурсу %s метод %s",
                    user_email,
                    user_role,
                    clear_path,
                    method.upper(),
                )
                raise HTTPException(status_code=403, detail="Forbidden")

            # Доступ разрешён - пишем debug
            logger.debug(
                "Доступ разрешён для пользователя '%s' (%s) к %s %s",
                user_email,
                user_role,
                clear_path,
                method.upper(),
            )
            return await call_next(request)

        # Обработка HTTP ошибок авторизации/доступа
        except HTTPException as e:
            logger.error("HTTPException: %s (%s %s)", e.detail, request.method, request.url.path)
            return JSONResponse(status_code=e.status_code, content={"detail": e.detail})

        # Специальная обработка истекшего токена
        except exceptions.ExpiredSignatureError as exc:
            logger.warning("Token expired при попытке доступа к %s", request.url.path)
            raise HTTPException(status_code=401, detail="Token expired") from exc

        # Обработка других ошибок токена
        except exceptions.JWTError as exc:
            logger.error("Invalid token при попытке доступа к %s", request.url.path)
            raise HTTPException(status_code=401, detail="Invalid token") from exc
