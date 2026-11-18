
import os
import hmac
import hashlib
import requests

from dotenv import load_dotenv

load_dotenv()

URL = "http://127.0.0.1:8000/webhooks/customer-events"
SECRET = os.getenv("WEBHOOK_SECRET")

payload = b'{"event":"customer.created","customer_id":1}'

signature = hmac.new(
    SECRET.encode("utf-8"),
    payload,
    hashlib.sha256
).hexdigest()

# Test 1: Valid signature
response = requests.post(
    URL,
    data=payload,
    headers={"X-Signature": signature},
    timeout=10
)
print("Valid signature:", response.status_code, response.json())

# Test 2: Tampered payload
response = requests.post(
    URL,
    data=b'{"event":"customer.deleted","customer_id":1}',
    headers={"X-Signature": signature},
    timeout=10
)
print("Tampered payload:", response.status_code, response.json())

# Test 3: Missing signature
response = requests.post(
    URL,
    data=payload,
    timeout=10
)
print("Missing signature:", response.status_code, response.json())
