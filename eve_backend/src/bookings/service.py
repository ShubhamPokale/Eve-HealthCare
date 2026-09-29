from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.bookings.exceptions import OfferingNotFound
from src.bookings.model import Booking
from src.diagnostics.models import CentreTestOffering


async def create_booking(
    session: AsyncSession,
    user_id: UUID,
    offering_id: UUID,
    appointment_at: datetime,
) -> Booking:
    offering = await session.get(CentreTestOffering, offering_id)
    if offering is None:
        raise OfferingNotFound()

    booking = Booking(
        user_id=user_id,
        offering_id=offering_id,
        appointment_at=appointment_at,
        amount=offering.price,
    )
    session.add(booking)
    await session.commit()
    await session.refresh(booking)
    return booking
