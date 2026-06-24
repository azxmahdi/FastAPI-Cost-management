from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Request,
    Response,
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timedelta, timezone

from account.schemas import (
    RegiterationSchema,
    LoginSchema,
)
from account.models import UserModel
from dependencies.database import get_db
from config.settings import settings
from account.managers import JWTManager
from dependencies.auth import get_current_user_from_cookie

router = APIRouter(prefix="/account/auth", tags=["account", "auth"])


def set_access_token_cookie(response: Response, access_token: str):

    expires_access = datetime.now(timezone.utc) + timedelta(
        seconds=settings.ACCESS_TOKEN_EXPIRATION
    )
    response.set_cookie(
        key=settings.ACCESS_TOKEN_COOKIE_NAME,
        value=access_token,
        expires=expires_access,
        httponly=True,
        secure=False,
        samesite="strict",
        path="/",
    )


def set_refresh_token_cookie(response: Response, refresh_token: str):
    expires_refresh = datetime.now(timezone.utc) + timedelta(
        seconds=settings.REFRESH_TOKEN_EXPIRATION
    )

    response.set_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_token,
        expires=expires_refresh,
        httponly=True,
        secure=False,
        samesite="strict",
        path="/",
    )


@router.post("/registeration")
def registeration(request: RegiterationSchema, db: Session = Depends(get_db)):
    if (
        db.query(UserModel)
        .where(UserModel.username == request.username)
        .one_or_none()
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="username already exists",
        )
    user_obj = UserModel(username=request.username)
    user_obj.set_password(request.password)
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)

    result = JWTManager.create_tokens_for_user(db, user_obj)

    response = JSONResponse(
        content={"detail": "user successfully login", **result},
        status_code=status.HTTP_200_OK,
    )
    set_access_token_cookie(response, result["access"])
    set_refresh_token_cookie(response, result["refresh"])

    return response


@router.post("/login")
def login(request: LoginSchema, db: Session = Depends(get_db)):

    statement = select(UserModel).where(UserModel.username == request.username)
    user_obj = db.execute(statement).scalar_one_or_none()

    if not (user_obj and user_obj.verify_password(request.password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username or password is wrong",
        )
    result = JWTManager.create_tokens_for_user(db, user_obj)
    response = JSONResponse(
        content={"detail": "user successfully login", **result},
        status_code=status.HTTP_200_OK,
    )
    set_access_token_cookie(response, result["access"])
    set_refresh_token_cookie(response, result["refresh"])
    return response


@router.post("/logout")
def logout(
    request: Request,
    auth_user: UserModel = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db),
):
    refresh_token_from_cookie = request.cookies.get(
        settings.REFRESH_TOKEN_COOKIE_NAME
    )
    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"detail": "successfully logout"},
    )
    if not refresh_token_from_cookie:
        if settings.ACCESS_TOKEN_COOKIE_NAME in request.cookies:
            response.delete_cookie(settings.ACCESS_TOKEN_COOKIE_NAME)
        return JSONResponse(
            {"message": "No active session found."},
            status_code=status.HTTP_200_OK,
        )
    JWTManager.logout(
        refresh_token_from_cookie, auth_user, response, request, db
    )
    return response
