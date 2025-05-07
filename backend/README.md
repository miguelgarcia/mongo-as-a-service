# Mongo as a Service (FastAPI)

This is a FastAPI application that allows authenticated users to manage metadata for "MongoDB instances" using a simple REST API. The app stores instance data in MongoDB and secures endpoints using an API key.

---

## Features

- API Key authentication (via `X-API-Key` header)
- CRUD operations for Mongo instance records
- MongoDB for storage

---

## Tech Stack

- FastAPI
- MongoDB
- Docker + Docker Compose
- Python 3.11

---

## Running Locally

```bash
uv run poe app
```

---

## Testing

The project includes comprehensive test coverage using pytest.

**Run tests**

```bash
uv run poe test
```

**Run tests with coverage report**

```bash
uv run poe test-cov
```