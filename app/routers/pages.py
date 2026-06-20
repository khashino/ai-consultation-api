from fastapi import APIRouter
from fastapi.responses import FileResponse


router = APIRouter(tags=["Pages"])


@router.get("/app")
def frontend_app():
    return FileResponse("static/index.html")


@router.get("/chat-demo")
def chat_demo():
    return FileResponse("static/embed-demo.html")