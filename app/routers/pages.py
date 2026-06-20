from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from app.core.security import require_admin


router = APIRouter(tags=["Pages"])


@router.get("/app")
def admin_dashboard(_: str = Depends(require_admin)):
    return FileResponse("static/index.html")


@router.get("/chat-demo")
def chat_demo():
    return FileResponse("static/embed-demo.html")