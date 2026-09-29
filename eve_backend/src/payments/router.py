import random
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import SessionFactory, get_db
from src.payments import service as payment_service
from src.payments.schemas import PaymentSimulateRequest, WebhookPayload, WebhookStatus

router = APIRouter(prefix="/payments", tags=["payments"])

SessionDep = Annotated[AsyncSession, Depends(get_db)]


@router.post(
    "/webhook",
    status_code=status.HTTP_200_OK,
    summary="Receive payment webhook",
    description="Endpoint called by the payment gateway to notify booking status changes.",
)
async def receive_webhook(
    payload: WebhookPayload,
    session: SessionDep,
) -> dict[str, str]:
    result = await payment_service.process_webhook(session, payload)
    return {"detail": result}


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Simulate a payment gateway checkout",
    description="Mock endpoint that simulates a third-party payment gateway. "
    "Randomly succeeds or fails, then triggers the webhook asynchronously.",
)
async def simulate_payment(
    payload: PaymentSimulateRequest,
    background_tasks: BackgroundTasks,
    session: SessionDep,
) -> dict[str, str]:
    # Randomly decide success or failure
    payment_status = (
        WebhookStatus.SUCCESS
        if random.random() < 0.5
        else WebhookStatus.FAILED
    )

    # Generate a fake provider event ID
    provider_event_id = str(uuid4())

    # Build the webhook payload
    webhook_payload = WebhookPayload(
        provider_event_id=provider_event_id,
        booking_id=payload.booking_id,
        status=payment_status,
    )

    # Schedule the webhook to run in the background
    background_tasks.add_task(
        _trigger_webhook,
        webhook_payload,
    )

    return {"detail": "Payment processing", "status": "accepted"}


async def _trigger_webhook(payload: WebhookPayload) -> None:
    """Background task that calls the webhook processor with its own session."""
    async with SessionFactory() as session:
        await payment_service.process_webhook(session, payload)
