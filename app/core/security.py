
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext

from .config import settings

ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Security:

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)

    @staticmethod
    def create_access_token(subject: str, minutes: Optional[int] = None) -> str:
        expires = datetime.now(timezone.utc) + timedelta(
            minutes=minutes or settings.access_token_expire_minutes
        )
        payload = {"sub": subject, "exp": expires, "type": "access"}
        return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)

    @staticmethod
    def create_refresh_token(subject: str, minutes: Optional[int] = None) -> str:
        expires = datetime.now(timezone.utc) + timedelta(
            minutes=minutes or settings.refresh_token_expire_minutes
        )
        payload = {"sub": subject, "exp": expires, "type": "refresh"}
        return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)

    @staticmethod
    def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
        try:
            return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        except JWTError:
            return None


security = Security()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    payload = security.decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload
