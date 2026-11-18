
import os

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")


def test_create_customer(client):
    response = client.post(
        "/customers",
        headers={"X-API-Key": API_KEY},
        json={
            "name": "Arun",
            "email": "arun@example.com",
            "phone": "9876543210",
            "city": "Chennai"
        }
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Arun"
    assert response.json()["email"] == "arun@example.com"



def test_get_customers(client):
    response = client.get(
        "/customers?page=1&per_page=10",
        headers={"X-API-Key": API_KEY}
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)



def test_get_customer_by_id(client):
    create_response = client.post(
        "/customers",
        headers={"X-API-Key": API_KEY},
        json={
            "name": "Rahul",
            "email": "rahul@example.com",
            "phone": "9876543210",
            "city": "Chennai"
        }
    )

    assert create_response.status_code == 201
    customer_id = create_response.json()["id"]

    response = client.get(
        f"/customers/{customer_id}",
        headers={"X-API-Key": API_KEY}
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Rahul"



def test_update_customer(client):
    create_response = client.post(
        "/customers",
        headers={"X-API-Key": API_KEY},
        json={
            "name": "Priya",
            "email": "priya@example.com",
            "phone": "9876543210",
            "city": "Chennai"
        }
    )

    assert create_response.status_code == 201
    customer_id = create_response.json()["id"]

    response = client.put(
        f"/customers/{customer_id}",
        headers={"X-API-Key": API_KEY},
        json={
            "name": "Priya Kumar",
            "city": "Bangalore"
        }
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Priya Kumar"
    assert response.json()["city"] == "Bangalore"



def test_delete_customer(client):
    create_response = client.post(
        "/customers",
        headers={"X-API-Key": API_KEY},
        json={
            "name": "Karthik",
            "email": "karthik@example.com",
            "phone": "9876543210",
            "city": "Chennai"
        }
    )

    assert create_response.status_code == 201
    customer_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/customers/{customer_id}",
        headers={"X-API-Key": API_KEY}
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/customers/{customer_id}",
        headers={"X-API-Key": API_KEY}
    )

    assert get_response.status_code == 404



def test_missing_api_key(client):
    response = client.get("/customers")

    assert response.status_code == 401
    assert response.json()["detail"] == "API key is missing"



def test_customer_not_found(client):
    response = client.get(
        "/customers/999",
        headers={"X-API-Key": API_KEY}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"



def test_duplicate_email(client):
    customer_data = {
        "name": "Arun",
        "email": "arun@example.com",
        "phone": "9876543210",
        "city": "Chennai"
    }

    first_response = client.post(
        "/customers",
        headers={"X-API-Key": API_KEY},
        json=customer_data
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/customers",
        headers={"X-API-Key": API_KEY},
        json=customer_data
    )

    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Email already exists"



def test_invalid_customer_data(client):
    response = client.post(
        "/customers",
        headers={"X-API-Key": API_KEY},
        json={
            "name": "Arun",
            "email": "invalid-email",
            "phone": "9876543210",
            "city": "Chennai"
        }
    )

    assert response.status_code == 422
