from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import service as auth_service
from src.auth.exceptions import InvalidCredentials
from src.auth.models import User
from src.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

TokenDep = Annotated[str, Depends(oauth2_scheme)]
SessionDep = Annotated[AsyncSession, Depends(get_db)]


async def parse_jwt_data(token: TokenDep) -> UUID:
    return auth_service.decode_access_token(token)


async def get_current_user(
    user_id: Annotated[UUID, Depends(parse_jwt_data)],
    session: SessionDep,
) -> User:
    user = await auth_service.get_by_id(session, user_id)
    if user is None:
        raise InvalidCredentials()
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
