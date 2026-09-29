# EVE Healthcare - Diagnostic Booking Service

A robust backend service for diagnostic test bookings and simulated payments, built with FastAPI and PostgreSQL.

## Architecture & Engineering Decisions

* **Database-First Data Integrity:** Enforced unique constraints (`provider_event_id`) and strict foreign keys (`RESTRICT` on deletions) to ensure impossible states cannot exist.
* **Webhook Idempotency:** The payment webhook endpoint is strictly idempotent. It uses a single-transaction pattern with a `UNIQUE` constraint on the payment event ID, paired with a `SELECT ... FOR UPDATE` row-level lock on the booking to prevent race conditions during concurrent webhook delivery.
* **Audit-Trail State Machine:** Terminal booking states (`CONFIRMED`, `FAILED`, `CANCELLED`) are immutable. Delayed or phantom webhooks record the payment event for reconciliation but do not corrupt the booking state machine.
* **N+1 Query Prevention:** `GET /centres/` utilizes SQLAlchemy 2.0 `joinedload` and `unique()` to fetch nested test offerings in a single database roundtrip.

## Tech Stack

* **Framework:** FastAPI
* **Database:** PostgreSQL (via asyncpg)
* **ORM:** SQLAlchemy 2.0 (Async)
* **Authentication:** JWT (PyJWT + passlib)
* **Testing:** Pytest + httpx

## Setup & Running Locally

Clone & Environment
``` bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

```


Ensure you have PostgreSQL installed and running. Create a local database for the project
``` bash  
createdb eve_db
```
Create a .env file in the project root directory and configure your environment variables:
``` bash 
DATABASE_URL=postgresql+asyncpg://your_db_user:your_db_password@localhost:5432/eve_db
AUTH_JWT_SECRET=your-super-secret-key-change-in-production
AUTH_JWT_EXP_MINUTES=60
```
Start the FastAPI application:
``` bash 
uvicorn src.main:app --reload
```

The API will be available at http://localhost:8000. You can view the interactive Swagger documentation at http://localhost:8000/docs

Execute the test suite using pytest:
``` bash 
pytest -v
```
## Assumptions Made
Dynamic Pricing: Test prices are not globally fixed; they vary depending on the diagnostic centre offering them. Therefore, prices are stored in an association table (centre_test_offering) and locked into the booking table at the time of creation to protect historical records from future price changes.

Immutable State Machine: Terminal booking states (CONFIRMED, FAILED, CANCELLED) are permanent. If a user's payment fails, the frontend must generate a new booking for a retry. This preserves the historical audit trail of failed attempts.

Phantom Webhook Processing: If a webhook arrives for a booking that has already transitioned to a terminal state (e.g., CANCELLED), the webhook is still processed and the Payment event is logged for financial reconciliation, but the booking state itself is strictly preserved.

Simulated Webhook Infrastructure: FastAPI's BackgroundTasks is utilized purely to simulate the asynchronous nature of a third-party payment gateway for this assignment. In a real-world production environment, this would be replaced with a persistent message broker (e.g., Celery, RabbitMQ) to handle retries and backpressure safely.

Data Privacy: Authorization checks are performed directly at the database query level to prevent Insecure Direct Object Reference (IDOR) vulnerabilities. Requesting an unauthorized resource returns a standard 404 rather than a 403 to avoid leaking the existence of other users' bookings.


## What I would improve with more time

Background Task Queue: Migrate the mock payment simulator to a persistent queue (like Celery/Redis) to handle backpressure and retry logic safely.

Alembic Migrations: Implement Alembic for version-controlled database schema evolution.

Dedicated Event Ledger: Move from a simple UNIQUE constraint to a dedicated webhook_events table for full event sourcing and replayability
