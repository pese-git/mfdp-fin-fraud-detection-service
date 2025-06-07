from typing import Optional

from fastapi import HTTPException, Request, status
from fastapi.openapi.models import OAuthFlowPassword
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from src.services.logging.logging import get_logger


class OAuth2PasswordBearerWithCookie(OAuth2):
    """
    This class is taken directly from FastAPI:
    https://github.com/tiangolo/fastapi/blob/26f725d259c5dbe3654f221e608b14412c6b40da/fastapi/security/oauth2.py#L140-L171

    The only change made is that authentication is taken from a cookie
    instead of from the header!
    """

    logger = get_logger(logger_name="cookieauth")

    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[dict[str, str]] = None,
        description: Optional[str] = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        password_flow = OAuthFlowPassword(tokenUrl=tokenUrl, scopes=scopes)
        flows = OAuthFlowsModel(password=password_flow)
        super().__init__(
            flows=flows,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: Optional[str] = request.cookies.get("access_token")
        self.logger.debug(
            "Попытка получения access_token из cookies: %r", authorization
        )
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            self.logger.warning(
                "Неудачная попытка аутентификации через cookies. Authorization: %r",
                authorization,
            )
            if self.auto_error:
                self.logger.error("Рaising HTTPException: Not authenticated")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        self.logger.info("Успешно извлечён токен из cookies")
        return param
