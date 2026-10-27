
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture
def valid_transaction():
    return {
        "transaction_id": "TXN-1001",
        "amount": 125.50,
        "currency": "SGD",
        "sender_account": "ACC-001",
        "receiver_account": "ACC-002",
    }


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_valid_transaction(valid_transaction):
    response = client.post("/validate", json=valid_transaction)

    assert response.status_code == 200
    assert response.json()["valid"] is True
    assert response.json()["transaction"]["currency"] == "SGD"


def test_zero_amount_is_rejected(valid_transaction):
    valid_transaction["amount"] = 0

    response = client.post("/validate", json=valid_transaction)

    assert response.status_code == 422


def test_negative_amount_is_rejected(valid_transaction):
    valid_transaction["amount"] = -10

    response = client.post("/validate", json=valid_transaction)

    assert response.status_code == 422


def test_unsupported_currency_is_rejected(valid_transaction):
    valid_transaction["currency"] = "XYZ"

    response = client.post("/validate", json=valid_transaction)

    assert response.status_code == 422


def test_same_sender_and_receiver_is_rejected(valid_transaction):
    valid_transaction["receiver_account"] = "ACC-001"

    response = client.post("/validate", json=valid_transaction)

    assert response.status_code == 422


def test_missing_transaction_id_is_rejected(valid_transaction):
    del valid_transaction["transaction_id"]

    response = client.post("/validate", json=valid_transaction)

    assert response.status_code == 422


def test_blank_transaction_id_is_rejected(valid_transaction):
    valid_transaction["transaction_id"] = "   "

    response = client.post("/validate", json=valid_transaction)

    assert response.status_code == 422

def test_jenkins_failure_demo():
    assert 1 == 2