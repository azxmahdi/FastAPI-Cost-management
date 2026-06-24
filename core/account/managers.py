import jwt
import uuid
from fastapi import HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from sqlalchemy import select

from config.settings import settings
from datetime import datetime, timedelta, timezone
from account.models import UserModel, RefreshTokenModel


class JWTManager:

    @staticmethod
    def create_tokens_for_user(
        db: Session, user: UserModel, access_payload: dict = {}
    ) -> dict:
        now = datetime.now(timezone.utc)

        access_payload.update(
            {
                "user_id": user.id,
                "exp": now
                + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRATION),
                "token_type": "access",
            }
        )
        access_token = jwt.encode(
            access_payload, settings.SECCRET_KEY, algorithm="HS256"
        )

        refresh_token_uuid = str(uuid.uuid4())
        refresh_payload = {
            "user_id": user.id,
            "exp": now + timedelta(seconds=settings.REFRESH_TOKEN_EXPIRATION),
            "jti": refresh_token_uuid,
            "token_type": "refresh",
        }
        refresh_token = jwt.encode(
            refresh_payload, settings.SECCRET_KEY, "HS256"
        )
        refresh_token_obj = RefreshTokenModel(
            expires_at=refresh_payload["exp"]
        )
        refresh_token_obj.token_hash = refresh_token_obj.hash_token(
            refresh_token
        )
        db.add(refresh_token_obj)
        db.commit()
        db.refresh(refresh_token_obj)
        return {
            "access": str(access_token),
            "refresh": str(refresh_token),
            "access_expires_in": settings.ACCESS_TOKEN_EXPIRATION,
            "refresh_expires_in": settings.REFRESH_TOKEN_EXPIRATION,
            "token_type": "Bearer",
        }

    @staticmethod
    def verify_token(token: str, token_type_expected: str):
        try:
            data = jwt.decode(token, settings.SECCRET_KEY, "HS256")

            token_type = data.get("token_type")
            if not (data.get("user_id") and data.get("exp") and token_type):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token is missing required claims (user_id, exp, "
                    "token_type).",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            if token_type != token_type_expected:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type. Expected "
                    f"'{token_type_expected}', but got '{token_type}'.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return data
        except (
            jwt.exceptions.InvalidSignatureError,
            jwt.exceptions.ExpiredSignatureError,
        ) as e:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Could not validate credentials: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred: {str(e)}",
            )

    @staticmethod
    def create_access_token(user: UserModel, access_payload: dict = {}):
        now = datetime.now(timezone.utc)

        access_payload.update(
            {
                "user_id": user.id,
                "exp": now
                + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRATION),
                "token_type": "access",
            }
        )
        access_token = jwt.encode(
            access_payload, settings.SECCRET_KEY, algorithm="HS256"
        )

        return str(access_token)

    @staticmethod
    def logout(
        refresh_token: str,
        user: UserModel,
        response: Response,
        request: Request,
        db: Session,
    ) -> None:
        JWTManager.verify_token(refresh_token, "refresh")

        token_hash = RefreshTokenModel.hash_token(refresh_token)
        statement = select(RefreshTokenModel).where(
            RefreshTokenModel.token_hash == token_hash,
            RefreshTokenModel.user_id == user.id,
            RefreshTokenModel.expires_at < datetime.now(timezone.utc),
            RefreshTokenModel.revoked is False
        )
        refresh_token_obj = db.execute(statement).scalar_one_or_none()
        if refresh_token_obj:
            refresh_token_obj.revoked is True
            db.commit()
            db.refresh(refresh_token_obj)

        response.delete_cookie(settings.REFRESH_TOKEN_COOKIE_NAME)
        if settings.ACCESS_TOKEN_COOKIE_NAME in request.cookies:
            response.delete_cookie(settings.ACCESS_TOKEN_COOKIE_NAME)
