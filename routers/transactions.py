from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import models
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/transactions", tags=["Transactions"])

class TransactionCreate(BaseModel):
    amount: float
    type: str
    description: Optional[str] = None

@router.post("/")
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    new_transaction = models.Transaction(
        amount=transaction.amount,
        type=models.TransactionType[transaction.type],
        description=transaction.description
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    return new_transaction

@router.get("/")
def get_transactions(db: Session = Depends(get_db)):
    return db.query(models.Transaction).all()