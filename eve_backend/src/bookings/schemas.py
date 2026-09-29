from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from src.bookings.model import BookingStatus


class BookingCreate(BaseModel):
    offering_id: UUID
    appointment_at: datetime

    @field_validator("appointment_at")
    @classmethod
    def appointment_must_be_in_future(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        if v <= datetime.now(timezone.utc):
            raise ValueError("Appointment time must be in the future")
        return v


class BookingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    offering_id: UUID
    amount: Decimal
    status: BookingStatus
    appointment_at: datetime
