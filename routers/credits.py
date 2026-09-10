from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/credits", tags=["Credits"])

class CustomerCreate(BaseModel):
    name: str
    phone: Optional[str] = None

class CreditCreate(BaseModel):
    customer_id: int
    amount_owed: float

class PaymentCreate(BaseModel):
    amount_paid: float

@router.post("/customers/")
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    new_customer = models.Customer(name=customer.name, phone=customer.phone)
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer

@router.post("/{credit_id}/pay")
def make_payment(credit_id: int, payment: PaymentCreate, db: Session = Depends(get_db)):
    credit = db.query(models.CreditRecord).filter(models.CreditRecord.id == credit_id).first()
    if not credit:
        raise HTTPException(status_code=404, detail="Credit record not found")
    new_payment = models.CreditPayment(credit_record_id=credit_id, amount_paid=payment.amount_paid)
    db.add(new_payment)
    total_paid = sum(p.amount_paid for p in credit.payments) + payment.amount_paid
    if total_paid >= credit.amount_owed:
        credit.status = models.CreditStatus.settled
    db.commit()
    return {"message": "Payment recorded", "total_paid": total_paid, "status": credit.status}

@router.post("/")
def create_credit(credit: CreditCreate, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.id == credit.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    new_credit = models.CreditRecord(customer_id=credit.customer_id, amount_owed=credit.amount_owed)
    db.add(new_credit)
    db.commit()
    db.refresh(new_credit)
    return new_credit

@router.get("/")
def get_outstanding_credits(db: Session = Depends(get_db)):
    return db.query(models.CreditRecord).filter(models.CreditRecord.status == models.CreditStatus.pending).all()



@router.get("/customers/search")
def search_customer_by_name(name: str, db: Session = Depends(get_db)):
    customers = db.query(models.Customer).filter(models.Customer.name.ilike(f"%{name}%")).all()
    if not customers:
        raise HTTPException(status_code=404, detail="No customer found with that name")
    return customers

@router.get("/customers/{customer_id}")
def get_customer_credits(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"customer": customer, "credits": customer.credits}

class CreditItemCreate(BaseModel):
    item_name: str
    quantity: float
    unit_price: float

@router.post("/{credit_id}/items")
def add_credit_item(credit_id: int, item: CreditItemCreate, db: Session = Depends(get_db)):
    credit = db.query(models.CreditRecord).filter(models.CreditRecord.id == credit_id).first()
    if not credit:
        raise HTTPException(status_code=404, detail="Credit record not found")
    total = item.quantity * item.unit_price
    new_item = models.CreditItem(
        credit_record_id=credit_id,
        item_name=item.item_name,
        quantity=item.quantity,
        unit_price=item.unit_price,
        total=total
    )
    db.add(new_item)
    credit.amount_owed += total
    db.commit()
    db.refresh(new_item)
    return new_item

@router.get("/customers/{customer_id}/full")
def get_customer_full_profile(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    credits = db.query(models.CreditRecord).filter(models.CreditRecord.customer_id == customer_id).all()
    result = []
    for credit in credits:
        payments = db.query(models.CreditPayment).filter(models.CreditPayment.credit_record_id == credit.id).all()
        items = db.query(models.CreditItem).filter(models.CreditItem.credit_record_id == credit.id).all()
        result.append({
            "id": credit.id,
            "amount_owed": credit.amount_owed,
            "status": credit.status.value,
            "created_at": credit.created_at,
            "items": [{"id": i.id, "item_name": i.item_name, "quantity": i.quantity, "unit_price": i.unit_price, "total": i.total} for i in items],
            "payments": [{"id": p.id, "amount_paid": p.amount_paid, "date_paid": p.date_paid} for p in payments]
        })
    return {"customer": {"id": customer.id, "name": customer.name, "phone": customer.phone}, "credits": result}

@router.post("/{credit_id}/clear")
def clear_debt(credit_id: int, db: Session = Depends(get_db)):
    credit = db.query(models.CreditRecord).filter(models.CreditRecord.id == credit_id).first()
    if not credit:
        raise HTTPException(status_code=404, detail="Credit record not found")
    credit.status = models.CreditStatus.settled
    db.commit()
    return {"message": "Debt cleared successfully"}


