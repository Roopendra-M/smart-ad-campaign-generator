from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Dict, Any

from . import auth
from . import models
from .ai_service import get_ai_service   # ✅ FIXED IMPORT

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/landing", response_class=HTMLResponse)
async def landing_page_redirect():
    return RedirectResponse(url="/", status_code=303)


@router.get("/signup", response_class=HTMLResponse)
async def signup_form(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@router.post("/signup", response_class=HTMLResponse)
async def signup(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    full_name: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db=Depends(models.get_db),
):
    if password != confirm_password:
        return templates.TemplateResponse(
            "signup.html",
            {"request": request, "error": "Passwords do not match"},
        )

    success, result = await auth.create_user(db, username, email, full_name, password)
    if not success:
        return templates.TemplateResponse(
            "signup.html",
            {"request": request, "error": result},
        )

    return RedirectResponse(
        "/login?success=Account+created+successfully.+Please+log+in.",
        status_code=303,
    )


@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db=Depends(models.get_db),
):
    user = await auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        return RedirectResponse(
            url="/login?error=Invalid+credentials", status_code=303
        )

    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user["username"]},
        expires_delta=access_token_expires,
    )

    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    return response


@router.get("/api/campaign-suggestion")
async def get_campaign_suggestion(
    request: Request,
    business_type: str = Query(None),
    db=Depends(models.get_db),
):
    try:
        # Optional authentication
        try:
            await auth.get_current_user(request=request, db=db)
        except:
            pass

        print(
            f"Campaign suggestion requested - Business type: {business_type or 'Not specified'}"
        )

        # ✅ CREATE FRESH AI SERVICE (NO CACHING)
        ai_service = get_ai_service()

        suggestion = await ai_service.get_campaign_suggestion(business_type)

        print("Campaign suggestion generated successfully")

        return JSONResponse(content=suggestion)

    except Exception as e:
        print("AI service error:", str(e))
        return JSONResponse(
            status_code=500,
            content={
                "error": "Could not generate campaign suggestion",
                "message": "AI service unavailable. Check GEMINI_API_KEY and model configuration.",
            },
        )
