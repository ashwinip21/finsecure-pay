FinSecure Pay — Transaction Validation API
<<<<<<< HEAD
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
=======
1. Overview

FinSecure Pay is a transaction validation REST API developed as part of a DevOps capstone project. The application provides a health-check endpoint and validates payment transaction requests against defined business rules.

This project demonstrates application development, automated testing, source control, and preparation for containerization and CI/CD deployment.

2. Technology Stack
Python 3: Application programming language.
FastAPI: REST API framework.
Pydantic: Request data validation.
Uvicorn: ASGI server for running the application.
pytest: Automated testing framework.
HTTPX: Supports API testing through FastAPI's test client.
Git and GitHub: Source control and repository hosting.
3. Technology Choice

Python and FastAPI were selected as alternatives to the recommended Spring Boot and Maven stack because they enable rapid API development, structured request validation, and automated testing.

pytest provides unit-testing capabilities equivalent in purpose to JUnit 5. The application can be containerized with Docker, deployed to Kubernetes, and integrated into a CI/CD pipeline.

4. Project Structure
finsecure-pay/
├── app/
│   ├── __init__.py
│   └── main.py
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── .gitignore
├── README.md
└── requirements.txt


The .venv/ directory contains the local Python virtual environment and should not be committed to Git.

5. Prerequisites

Ensure the following are installed:

Python 3.10 or a compatible newer version
Git
Visual Studio Code (recommended)

The project was developed and tested on macOS using Python 3.14.

6. Setup and Installation
Step 1: Clone the repository

Replace YOUR_USERNAME with your GitHub username.

git clone https://github.com/YOUR_USERNAME/finsecure-pay.git
cd finsecure-pay
Step 2: Create a virtual environment
python3 -m venv .venv
Step 3: Activate the virtual environment

On macOS or Linux:

source .venv/bin/activate
Step 4: Install dependencies
python -m pip install -r requirements.txt
7. Running the Application

Start the development server:
>>>>>>> 218b12c (Document setup and project dependencies)

python -m uvicorn app.main:app --reload


<<<<<<< HEAD
Open the interactive API documentation at http://127.0.0.1:8000/docs.

Run Tests
python -m pytest -v
Project Scope

This implementation demonstrates basic transaction validation. It does not perform actual payment processing, authorization, or fraud detection.
=======
The application runs locally at:

http://127.0.0.1:8000

Interactive API documentation is available at:

http://127.0.0.1:8000/docs

Stop the server by pressing Ctrl + C in the terminal.

8. API Endpoints
GET /health

Checks whether the API responds successfully.

Example response:

{
  "status": "healthy"
}


Expected HTTP status: 200 OK.

POST /validate

Validates a transaction request.

Example request:

{
  "transaction_id": "TXN-1001",
  "amount": 125.50,
  "currency": "SGD",
  "sender_account": "ACC-001",
  "receiver_account": "ACC-002"
}


Example successful response:

{
  "valid": true,
  "message": "Transaction passed validation",
  "transaction": {
    "transaction_id": "TXN-1001",
    "amount": 125.5,
    "currency": "SGD",
    "sender_account": "ACC-001",
    "receiver_account": "ACC-002"
  }
}


Expected HTTP status: 200 OK.

Invalid requests return HTTP 422 Unprocessable Entity with details of the validation errors.

9. Transaction Validation Rules

The application implements the following validation rules:

Transaction amount must be greater than zero.
Transaction amount must be a finite number.
Currency must be SGD, USD, or EUR.
Transaction ID must not be blank and must not exceed 100 characters.
Sender and receiver account identifiers must not be blank and must not exceed 100 characters.
Sender and receiver accounts must be different.
Required fields must be provided.

The API uses Pydantic validation to reject invalid requests before the endpoint processes them.

10. Automated Testing

The project uses pytest and FastAPI's test client to test the API.

Run all tests:

python -m pytest -v


Generate a JUnit-compatible XML test report:

python -m pytest -v --junitxml=test-results.xml


The automated test suite covers:

Health endpoint response
Successful transaction validation
Rejection of zero and negative amounts
Rejection of unsupported currencies
Rejection of identical sender and receiver accounts
Rejection of missing transaction identifiers
Rejection of blank transaction identifiers

Initial test result: 8 tests passed.

Run the tests again after making code changes to confirm the current result.

11. Build and Syntax Verification

Check Python source files for syntax errors:

python -m compileall app tests


This command verifies that the Python files can be compiled. It does not create a distributable application package.

12. Version Control

The project uses Git for source control and GitHub for remote repository hosting.

Check repository status:

git status


View recent commits:

git log --oneline


Commit and push changes:

git add .
git commit -m "Describe your changes"
git push origin main


Review .gitignore before staging files to ensure that virtual environments, caches, coverage reports, and secrets are excluded.

13. Task Scope and Limitations

This application demonstrates basic transaction validation for educational purposes.

It does not perform actual payment processing, authentication, authorization, fraud detection, database persistence, or financial settlement.

Further security controls and operational capabilities will be addressed in subsequent project stages, including containerization, CI/CD automation, security scanning, Kubernetes deployment, monitoring, logging, and alerting.
>>>>>>> 218b12c (Document setup and project dependencies)
