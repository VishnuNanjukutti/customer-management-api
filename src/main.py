
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from src.database import get_db

app = FastAPI(title="Customer Management API")


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    db.execute(__import__("sqlalchemy").text("SELECT 1"))

    return {
        "status": "healthy",
        "database": "connected"
    }
