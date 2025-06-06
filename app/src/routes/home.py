import os
from pathlib import Path
from typing import Any
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import markdown
from src.auth.authenticate import authenticate_via_cookies
from src.services.logging.logging import get_logger

from src.models.user import User

home_route = APIRouter()

static_dir = Path(__file__).parent.parent / "static"

# Jinja2 templates
template_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=template_dir)

# Инициализация логгера для этого модуля
logger = get_logger(logger_name="routes.home")


@home_route.get("/", tags=["Home"])
async def index(
    request: Request, current_user: User = Depends(authenticate_via_cookies)
) -> Any:
    # Путь к Markdown файлу
    markdown_file_path: str = os.path.join(static_dir, "home_page_content.md")
    html_content: str = ""

    # Проверяем, существует ли файл
    if not os.path.exists(markdown_file_path):
        html_content = "<h1>Markdown file not found.</h1>"
        logger.error("Markdown файл '%s' не найден при обращении к /", markdown_file_path)
    else:
        try:
            # Чтение и обработка Markdown файла
            with open(markdown_file_path, "r", encoding="utf-8") as md_file:
                markdown_content = md_file.read()
                # Конвертация Markdown в HTML
                html_content = markdown.markdown(markdown_content)
            logger.debug("Markdown файл '%s' успешно загружен и отрендерен.", markdown_file_path)
        except Exception as e:
            logger.exception("Ошибка при чтении Markdown файла '%s': %s", markdown_file_path, e)
            html_content = "<h1>Error loading content.</h1>"

    logger.info(
        "Пользователь '%s' (id=%s) открыл главную страницу '/'",
        getattr(current_user, "name", "anonymous"),
        getattr(current_user, "id", "unknown"),
    )
    context = {"user": current_user, "request": request, "content": html_content}
    return templates.TemplateResponse("index.html", context)


@home_route.get("/logout", response_class=HTMLResponse)
async def login_get() -> Any:
    logger.info("Пользователь вышел из системы (logout).")
    response = RedirectResponse(url="/")
    response.delete_cookie("access_token")
    return response
