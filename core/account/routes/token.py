from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timezone

from account.schemas import (
    RefreshAccessTokenSchema,
    AccessTokenVerifySchema,
)
from account.models import UserModel, RefreshTokenModel
from dependencies.database import get_db
from config.settings import settings
from account.managers import JWTManager
from account.routes.auth import set_access_token_cookie

router = APIRouter(prefix="/account/token", tags=["account", "token"])


@router.post("/refresh")
def recover_access_token(
    request: RefreshAccessTokenSchema, db: Session = Depends(get_db)
):
    token_hash = RefreshTokenModel.hash_token(request.refresh_token)
    now = datetime.now(timezone.utc)
    statement = select(RefreshTokenModel).where(
        RefreshTokenModel.token_hash == token_hash,
        RefreshTokenModel.revoked is False,
        RefreshTokenModel.expires_at > now,
    )
    refresh_token_obj = db.execute(statement).scalar_one_or_none()
    if not refresh_token_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired",
        )
    access_token = JWTManager.create_access_token(refresh_token_obj.user)

    return JSONResponse(
        content={
            "detail": "access tokens successfully restored",
            "access": access_token,
        }
    )


@router.post("refresh/cookie")
def recover_access_token_with_cookie(
    request: Request, db: Session = Depends(get_db)
):
    refresh_token = request.cookies.get(settings.REFRESH_TOKEN_COOKIE_NAME)

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found",
        )
    data = JWTManager.verify_token(refresh_token, "refresh")
    statement = select(UserModel).where(UserModel.id == data["user_id"])
    user = db.execute(statement).scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not founded"
        )
    access_token = JWTManager.create_access_token(user)
    response = JSONResponse(
        content={
            "detail": "access tokens successfully restored",
            "access": access_token,
        }
    )
    set_access_token_cookie(response, access_token)
    return response


@router.post("/token/verify")
def access_token_verify(request: AccessTokenVerifySchema):
    data = JWTManager.verify_token(request.access_roken, "access")
    data["valid"] = True
    return data
