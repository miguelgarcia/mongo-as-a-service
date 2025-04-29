# Mongo as a Service (FastAPI)

# TODO

* service layer [DONE]
* Provisioner class [DOING]

* black
* typing
* mypy

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

**Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate
```

**Install dependencies**

```bash
pip install -r requirements.txt
```

**Run app**

```bash
make run
```

---

## Testing

The project includes comprehensive test coverage using pytest.

**Run tests**

```bash
make test
```

**Run tests with coverage report**

```bash
make test-cov
```

**Generate HTML coverage report**

```bash
make coverage-html
```

This will create a `htmlcov` directory with an HTML report of your test coverage.

---

## Test Structure

The test suite includes:

- Unit tests for CRUD operations
- Unit tests for API routes
- Authentication tests
- Integration tests for the API endpoints

All tests use pytest fixtures to mock MongoDB and provide consistent test data.