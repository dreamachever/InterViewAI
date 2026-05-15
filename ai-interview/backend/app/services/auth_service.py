from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


class AuthService:
    def __init__(self, db: Session):
        self.users = UserRepository(db)

    def register(self, payload: RegisterRequest) -> User:
        email = payload.email.strip().lower()
        if self.users.get_by_email(email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        user = User(
            email=email,
            password_hash=hash_password(payload.password),
            nickname=payload.nickname.strip() if payload.nickname else None,
        )
        return self.users.create(user)

    def login(self, payload: LoginRequest) -> TokenResponse:
        email = payload.email.strip().lower()
        user = self.users.get_by_email(email)
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
        return TokenResponse(access_token=create_access_token(user.id))
