from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from dependencies.database import get_db
from config.settings import settings
from account.managers import JWTManager
from account.models import UserModel


def get_current_user_from_cookie(
    request: Request, db: Session = Depends(get_db)
):
    access_token = request.cookies.get(settings.ACCESS_TOKEN_COOKIE_NAME)
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token not found in cookies",
            headers={"WWW-Authenticate": "Bearer"},
        )
    data = JWTManager.verify_token(access_token, "access")
    statement = select(UserModel).where(UserModel.id == data["user_id"])
    user = db.execute(statement).scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not founded"
        )

    return user
