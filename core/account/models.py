import hashlib
from sqlalchemy import (
    Column,
    String,
    TIMESTAMP,
    Boolean,
    Integer,
    DateTime,
    func,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from config.database import Base


class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(250), nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_date = Column(DateTime, server_default=func.now())
    updated_date = Column(
        DateTime, server_default=func.now(), server_onupdate=func.now()
    )

    costs = relationship("CostModel", back_populates="user", uselist=True)
    tokens = relationship(
        "RefreshTokenModel", back_populates="user", uselist=True
    )

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, plain_password: str) -> bool:
        return (
            hashlib.sha256(plain_password.encode()).hexdigest()
            == self.password
        )

    def set_password(self, plain_password: str) -> None:
        self.password = self.hash_password(plain_password)

    def __repr__(self):
        return f"<UserModel(id={self.id}, username='{self.username}'," \
            f"created_date='{self.created_date}')>"


class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"
    id = Column(
        Integer, primary_key=True, autoincrement=True, unique=True, index=True
    )
    token_hash = Column(String, nullable=False, unique=True, index=True)
    revoked = Column(Boolean, default=False)
    last_used_at = Column(TIMESTAMP(timezone=True), nullable=True)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("UserModel", back_populates="tokens", uselist=False)

    @staticmethod
    def hash_token(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    def verify_token(self, plain_token: str) -> bool:
        return (
            hashlib.sha256(plain_token.encode()).hexdigest() == self.token_hash
        )
