from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.diagnostics import service as diagnostics_service
from src.diagnostics.models import Centre
from src.diagnostics.schemas import CentreRead

router = APIRouter(prefix="/centres", tags=["centres"])

SessionDep = Annotated[AsyncSession, Depends(get_db)]


@router.get(
    "",
    response_model=list[CentreRead],
    summary="List diagnostic centres",
    description=(
        "Returns every centre with the tests it offers and each offering's price, "
        "so a client can render a booking menu from one response."
    ),
)
async def list_centres(session: SessionDep) -> Sequence[Centre]:
    return await diagnostics_service.list_centres(session)
