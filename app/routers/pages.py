from fastapi import APIRouter, Form, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse

from app.core.config import settings
from app.core.security import (
    create_admin_session_token,
    get_admin_username_from_request,
    verify_admin_credentials,
)


router = APIRouter(tags=["Pages"])


@router.get("/login")
def login_page(request: Request):
    username = get_admin_username_from_request(request)

    if username:
        return RedirectResponse(url="/app", status_code=303)

    return FileResponse("static/login.html")


@router.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...),
):
    if not verify_admin_credentials(username, password):
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid username or password."},
        )

    token = create_admin_session_token(username)

    response = RedirectResponse(url="/app", status_code=303)

    response.set_cookie(
        key=settings.admin_cookie_name,
        value=token,
        httponly=True,
        secure=settings.admin_cookie_secure,
        samesite="lax",
        max_age=60 * 60 * 8,
        path="/",
    )

    return response


@router.post("/logout")
def logout():
    response = JSONResponse(
        content={"message": "Signed out successfully."}
    )

    response.delete_cookie(
        key=settings.admin_cookie_name,
        path="/",
    )

    return response


@router.get("/app")
def admin_dashboard(request: Request):
    username = get_admin_username_from_request(request)

    if not username:
        return RedirectResponse(url="/login", status_code=303)

    return FileResponse("static/index.html")


@router.get("/chat-app")
def full_chat_page(request: Request):
    username = get_admin_username_from_request(request)

    if not username:
        return RedirectResponse(url="/login", status_code=303)

    return FileResponse("static/chat.html")


@router.get("/chat-demo")
def chat_demo():
    return FileResponse("static/embed-demo.html")