from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.auth import service as auth_service
from src.auth.schemas import UserCreate, Token

router = APIRouter(prefix="/auth", tags=["auth"])
SessionDep = Annotated[AsyncSession, Depends(get_db)]

@router.post(
    "/signup", 
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user"
)
async def signup(user_in: UserCreate, session: SessionDep) -> dict[str, str]:
    try:
        await auth_service.create_user(session, user_in)
        return {"detail": "User created successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(e)
        )

@router.post(
    "/login", 
    response_model=Token,
    summary="Login to get access token"
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep
) -> Token:
    # OAuth2PasswordRequestForm strictly uses "username" for the field, 
    # so we map the user's input email to form_data.username.
    user = await auth_service.get_user_by_email(session, form_data.username)
    
    if not user or not auth_service.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = auth_service.create_access_token(user.id)
    return Token(access_token=access_token)