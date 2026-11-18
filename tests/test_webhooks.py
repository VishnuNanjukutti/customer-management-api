
import os
import hmac
import hashlib
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")


# Test 1: Valid webhook signature
def test_valid_webhook_signature(client):
    payload = b'{"event":"customer.created","customer_id":1}'

    signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    response = client.post(
        "/webhooks/customer-events",
        content=payload,
        headers={"X-Signature": signature}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "accepted"


# Test 2: Tampered webhook payload
def test_tampered_webhook_signature(client):
    original_payload = b'{"event":"customer.created","customer_id":1}'
    tampered_payload = b'{"event":"customer.created","customer_id":999}'

    signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        original_payload,
        hashlib.sha256
    ).hexdigest()

    response = client.post(
        "/webhooks/customer-events",
        content=tampered_payload,
        headers={"X-Signature": signature}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid signature"


# Test 3: Missing webhook signature
def test_missing_webhook_signature(client):
    payload = b'{"event":"customer.created","customer_id":1}'

    response = client.post(
        "/webhooks/customer-events",
        content=payload
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid signature"
