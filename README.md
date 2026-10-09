# FastAPI Product API

This project is a layered FastAPI application for managing products and sellers.

## Structure

```text
app/
├── api/routes/       HTTP endpoints
├── core/             configuration and password hashing
├── db/               SQLAlchemy engine, sessions, and model registration
├── models/           database tables
├── schemas/          request and response validation
├── repositories/     database queries
└── services/         business logic
```

Routes only handle HTTP concerns. Services contain business logic, repositories
contain database access, SQLAlchemy models represent tables, and Pydantic
schemas validate API data.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

`.env` is intentionally ignored by Git because it may contain database
credentials. Keep `.env.example` updated with placeholder configuration for
other developers.

The default database is SQLite (`product.db`), so the project runs locally
without additional database setup. To use MySQL, set `DATABASE_URL` in `.env`:

```env
DATABASE_URL=mysql+pymysql://username:password@host:3306/database_name
```

## Run

```bash
uvicorn app.main:app --reload
```

Interactive API documentation is available at
`http://127.0.0.1:8000/docs`.

## Tests

Install dependencies and run the test suite from the project root:

```bash
python -m pip install -r requirements.txt
pytest
```

Tests use an isolated in-memory SQLite database and do not modify the local
development database.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/products` | Create a product |
| GET | `/products` | List products |
| GET | `/products/{product_id}` | Get a product |
| PUT | `/products/{product_id}` | Update a product |
| DELETE | `/products/{product_id}` | Delete a product |
| POST | `/sellers` | Create a seller |
| GET | `/sellers` | List sellers |
