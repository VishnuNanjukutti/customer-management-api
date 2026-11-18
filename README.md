
# Customer Management API

A REST API built with FastAPI, PostgreSQL, and SQLAlchemy for managing customer records.

## Features

- Create, read, update, and delete customers
- API key authentication
- Pagination and customer name search
- PostgreSQL database integration
- Alembic database migrations
- HMAC-SHA256 webhook signature verification
- Integration tests using pytest

## Technologies

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic
- pytest and pytest-cov

## Project Setup

1. Clone the repository.
2. Create and activate a Python virtual environment.
3. Install project dependencies.
4. Create a `.env` file using `.env.example` as a reference.
5. Configure the PostgreSQL database.
6. Run database migrations:

   python -m alembic upgrade head

7. Start the API:

   python -m uvicorn src.main:app --reload

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check |
| POST | /customers | Create customer |
| GET | /customers | List customers |
| GET | /customers/{id} | Get customer |
| PUT | /customers/{id} | Update customer |
| DELETE | /customers/{id} | Delete customer |
| POST | /webhooks/customer-events | Receive signed webhook |

## Authentication

Customer endpoints require the `X-API-Key` request header.

The API key is configured through the `.env` file.

## Webhook Security

Webhook requests are verified using HMAC-SHA256.

The signature must be provided in the `X-Signature` header.

Invalid or missing signatures return HTTP 401.

## Integration Tests

Integration tests use FastAPI TestClient and a separate PostgreSQL test database.

Configure `TEST_DATABASE_URL` in `.env` before running tests.

Run all tests with coverage:

    python -m pytest tests/ --cov=src -v

Latest local test results:

- 12 tests passed
- 90% total code coverage
- CRUD and authentication tests passed
- Webhook signature tests passed

## API Documentation

After starting the server, open:

http://127.0.0.1:8000/docs

## Author

Vishnu
