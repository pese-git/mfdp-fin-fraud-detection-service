from pathlib import Path
from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from src import schemas
from src.auth.authenticate import get_current_user_via_cookies


dashboard_route = APIRouter()
# Jinja2 templates
template_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=template_dir)


@dashboard_route.get("/dashboard")
async def read_dashboard(
    request: Request, current_user: schemas.User = Depends(get_current_user_via_cookies)
):
    context = {"user": current_user, "username": current_user.name, "request": request}
    return templates.TemplateResponse("dashboard.html", context)
