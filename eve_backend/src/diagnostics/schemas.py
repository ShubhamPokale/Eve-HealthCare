from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TestSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None = None


class OfferingRead(BaseModel):
    """A test as sold by a specific centre, with that centre's price."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    price: Decimal
    test: TestSummary


class CentreRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    location: str
    offerings: list[OfferingRead]
