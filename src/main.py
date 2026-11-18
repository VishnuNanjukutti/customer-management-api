
import os
import hmac
import hashlib
import logging

from fastapi import Request, BackgroundTasks, Header

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from src.schemas import CustomerUpdate

from src.models import Customer
from src.schemas import CustomerCreate, CustomerOut

from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.database import get_db
from src.auth import verify_api_key

app = FastAPI(title="Customer Management API")


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))

    return {
        "status": "healthy",
        "database": "connected"
    }


@app.post(
    "/customers",
    response_model=CustomerOut,
    status_code=status.HTTP_201_CREATED
)
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    new_customer = Customer(**customer.model_dump())

    db.add(new_customer)

    try:
        db.commit()
        db.refresh(new_customer)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email already exists"
        )

    return new_customer




@app.get("/customers", response_model=list[CustomerOut])
def get_customers(
    page: int = 1,
    per_page: int = 10,
    name: str | None = None,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    query = db.query(Customer)

    if name:
        query = query.filter(Customer.name.ilike(f"%{name}%"))

    skip = (page - 1) * per_page

    customers = (
        query
        .order_by(Customer.id)
        .offset(skip)
        .limit(per_page)
        .all()
    )

    return customers


@app.get("/customers/{id}", response_model=CustomerOut)
def get_customer(
    id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    customer = db.query(Customer).filter(Customer.id == id).first()

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return customer



@app.put("/customers/{id}", response_model=CustomerOut)
def update_customer(
    id: int,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    customer = db.query(Customer).filter(Customer.id == id).first()

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    update_data = customer_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(customer, key, value)

    try:
        db.commit()
        db.refresh(customer)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email already exists"
        )

    return customer



@app.delete("/customers/{id}", status_code=204)
def delete_customer(
    id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    customer = db.query(Customer).filter(Customer.id == id).first()

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    db.delete(customer)
    db.commit()

    return None



def process_customer_event(event_body: bytes):
    logging.info("Customer webhook event: %s", event_body.decode("utf-8", errors="replace"))


@app.post("/webhooks/customer-events")
async def receive_customer_event(
    request: Request,
    background_tasks: BackgroundTasks,
    x_signature: str | None = Header(default=None)
):
    body = await request.body()
    secret = os.getenv("WEBHOOK_SECRET")

    if not secret:
        raise HTTPException(
            status_code=500,
            detail="Webhook secret is not configured"
        )

    expected_signature = hmac.new(
        secret.encode("utf-8"),
        body,
        hashlib.sha256
    ).hexdigest()

    if not x_signature or not hmac.compare_digest(
        x_signature, expected_signature
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid signature"
        )

    background_tasks.add_task(process_customer_event, body)

    return {"status": "accepted"}
