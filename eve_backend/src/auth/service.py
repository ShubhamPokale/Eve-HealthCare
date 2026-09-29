from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.config import auth_settings
from src.auth.exceptions import InvalidCredentials
from src.auth.models import User

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from src.auth.schemas import UserCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def create_access_token(user_id: UUID) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=auth_settings.JWT_EXP_MINUTES),
    }
    return jwt.encode(
        payload,
        auth_settings.JWT_SECRET,
        algorithm=auth_settings.JWT_ALG,
    )


def decode_access_token(token: str) -> UUID:
    try:
        payload = jwt.decode(
            token,
            auth_settings.JWT_SECRET,
            algorithms=[auth_settings.JWT_ALG],
        )
        user_id = UUID(payload["sub"])
    except (InvalidTokenError, KeyError, TypeError, ValueError) as exc:
        raise InvalidCredentials() from exc
    return user_id


async def get_by_id(session: AsyncSession, user_id: UUID) -> User | None:
    return await session.get(User, user_id)


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    return await session.scalar(stmt)

async def create_user(session: AsyncSession, user_in: UserCreate) -> User:
    hashed_password = hash_password(user_in.password)
    new_user = User(
        email=user_in.email, 
        password_hash=hashed_password
    )
    session.add(new_user)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        # Raised if the unique constraint on the email column is violated
        raise ValueError("Email already registered")
    
    return new_user