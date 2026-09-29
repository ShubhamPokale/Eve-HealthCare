from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.bookings.model import Booking, BookingStatus, Payment, PaymentStatus
from src.payments.schemas import WebhookPayload


async def process_webhook(
    session: AsyncSession,
    payload: WebhookPayload,
) -> str:
    # Step 1: Query and lock the booking FIRST (FOR UPDATE).
    # If it doesn't exist, we bail out immediately — no Payment insert,
    # no ambiguity about what caused an IntegrityError later.
    stmt = (
        select(Booking)
        .where(Booking.id == payload.booking_id)
        .with_for_update()
    )
    booking = await session.scalar(stmt)

    if not booking:
        return "Invalid booking ID"

    # Step 2: State machine — only transition from PENDING
    if booking.status == BookingStatus.PENDING:
        if payload.status == WebhookStatus.SUCCESS:
            booking.status = BookingStatus.CONFIRMED
        else:
            booking.status = BookingStatus.FAILED

    # Step 3: Add the payment record
    payment = Payment(
        booking_id=payload.booking_id,
        provider_event_id=payload.provider_event_id,
        status=PaymentStatus(payload.status.value),
    )
    session.add(payment)

    # Step 4: Single commit for both operations.
    # If this fails with IntegrityError, we KNOW it's the unique constraint
    # on provider_event_id — because we already verified the booking exists
    # and locked it. No ambiguity.
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        return "Duplicate event ignored"

    return "Webhook processed"
