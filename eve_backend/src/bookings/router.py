from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import CurrentUser
from src.bookings import service as booking_service
from src.bookings.schemas import BookingCreate, BookingRead
from src.database import get_db

router = APIRouter(prefix="/bookings", tags=["bookings"])

SessionDep = Annotated[AsyncSession, Depends(get_db)]


@router.post(
    "",
    response_model=BookingRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a booking",
    description="Book an appointment for a diagnostic test offering.",
)
async def create_booking(
    payload: BookingCreate,
    user: CurrentUser,
    session: SessionDep,
) -> BookingRead:
    return await booking_service.create_booking(
        session=session,
        user_id=user.id,
        offering_id=payload.offering_id,
        appointment_at=payload.appointment_at,
    )
