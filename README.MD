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

1. **Clone & Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt