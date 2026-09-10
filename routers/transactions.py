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


@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    sales = db.query(models.Transaction).filter(models.Transaction.type == models.TransactionType.sale).all()
    expenses = db.query(models.Transaction).filter(models.Transaction.type == models.TransactionType.expense).all()
    pending_credits = db.query(models.CreditRecord).filter(models.CreditRecord.status == models.CreditStatus.pending).all()

    total_sales = sum(t.amount for t in sales)
    total_expenses = sum(t.amount for t in expenses)
    net_balance = total_sales - total_expenses
    total_outstanding = sum(c.amount_owed for c in pending_credits)

    return {
        "total_sales": total_sales,
        "total_expenses": total_expenses,
        "net_balance": net_balance,
        "total_outstanding_debt": total_outstanding
    }