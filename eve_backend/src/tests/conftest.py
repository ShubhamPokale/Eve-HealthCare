import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.main import app
from src.database import Base, get_db
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.bookings.model import Booking, BookingStatus
from src.database import SessionFactory
from src.diagnostics.models import Centre, CentreTestOffering, Test

# Use an in-memory SQLite database for fast async testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def db_session() -> AsyncSession:
    async with SessionFactory() as session:
        yield session


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    user = User(
        email="test@example.com",
        password_hash="fakehashedpassword",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_offering(db_session: AsyncSession) -> CentreTestOffering:
    centre = Centre(name="Test Centre", location="Test Location")
    test = Test(name="Test Panel", description="A test panel")
    db_session.add(centre)
    db_session.add(test)
    await db_session.commit()

    offering = CentreTestOffering(
        centre_id=centre.id,
        test_id=test.id,
        price=99.99,
    )
    db_session.add(offering)
    await db_session.commit()
    await db_session.refresh(offering)
    return offering


@pytest.fixture
async def test_booking(
    db_session: AsyncSession,
    test_user: User,
    test_offering: CentreTestOffering,
) -> Booking:
    booking = Booking(
        user_id=test_user.id,
        offering_id=test_offering.id,
        appointment_at="2027-01-01T10:00:00Z",
        amount=test_offering.price,
        status=BookingStatus.PENDING,
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)
    return booking