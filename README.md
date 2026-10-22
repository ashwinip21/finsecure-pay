FinSecure Pay — Transaction Validation API
Overview

FinSecure Pay is a transaction validation API developed as part of a DevOps capstone project. It provides a health endpoint and validates payment transaction requests using defined business rules.

Technology Stack
Python 3
FastAPI for REST API development
Pydantic for request validation
pytest for automated testing
Git and GitHub for version control
Technology Choice

Python and FastAPI were selected as alternatives to Spring Boot because they support rapid API development, structured request validation, and automated testing. pytest provides automated unit-testing capabilities equivalent in purpose to JUnit 5. The Python implementation can be containerized and deployed to Kubernetes and integrated into a CI/CD pipeline.

Endpoints
GET /health — returns the API health status.
POST /validate — validates a transaction request.
Validation Rules
Transaction amount must be greater than zero.
Currency must be SGD, USD, or EUR.
Transaction ID, sender account, and receiver account must not be blank.
Sender and receiver accounts must be different.
Required fields must be present.
Run Locally

Install dependencies:

python -m pip install -r requirements.txt


Start the API:

python -m uvicorn app.main:app --reload


Open the interactive API documentation at http://127.0.0.1:8000/docs.

Run Tests
python -m pytest -v
Project Scope

This implementation demonstrates basic transaction validation. It does not perform actual payment processing, authorization, or fraud detection.
