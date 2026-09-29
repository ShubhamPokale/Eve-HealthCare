from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.diagnostics.models import Centre, CentreTestOffering


async def list_centres(session: AsyncSession) -> Sequence[Centre]:
    stmt = (
        select(Centre)
        .options(joinedload(Centre.offerings).joinedload(CentreTestOffering.test))
        .order_by(Centre.name)
    )
    result = await session.scalars(stmt)
    return result.unique().all()
