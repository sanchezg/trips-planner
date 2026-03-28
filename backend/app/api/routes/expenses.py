from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models.expense import Expense
from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.repositories.trip_repository import TRIP_ROLE_EDITOR, get_for_user, get_trip_for_min_role
from app.schemas.expense import ExpenseCreate, ExpenseRead

router = APIRouter()


@router.get("", response_model=list[ExpenseRead])
def list_expenses(trip_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = get_for_user(db, trip_id, current_user.id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return db.query(Expense).filter(Expense.trip_id == trip_id).order_by(Expense.incurred_on.desc()).all()


@router.post("", response_model=ExpenseRead)
def create_expense(payload: ExpenseCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = get_trip_for_min_role(db, payload.trip_id, current_user.id, TRIP_ROLE_EDITOR)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    expense = Expense(**payload.model_dump())
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense
