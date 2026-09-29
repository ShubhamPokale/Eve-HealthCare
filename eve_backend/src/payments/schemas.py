from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel


class WebhookStatus(StrEnum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class WebhookPayload(BaseModel):
    provider_event_id: str
    booking_id: UUID
    status: WebhookStatus


class PaymentSimulateRequest(BaseModel):
    booking_id: UUID
