from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import date

from app.database import get_db
from app.models import Employee
from app.schemas import EmployeeCreate, EmployeeUpdate, Employee as EmployeeSchema, EmployeeList

router = APIRouter()


@router.get("", response_model=EmployeeList)
async def get_employees(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get list of all employees."""
    result = await db.execute(select(Employee).offset(skip).limit(limit))
    employees = result.scalars().all()

    # Get total count
    count_result = await db.execute(select(Employee))
    total = len(count_result.scalars().all())

    return EmployeeList(employees=employees, total=total)


@router.get("/{employee_id}", response_model=EmployeeSchema)
async def get_employee(employee_id: int, db: AsyncSession = Depends(get_db)):
    """Get employee by ID."""
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    return employee


@router.post("", response_model=EmployeeSchema, status_code=status.HTTP_201_CREATED)
async def create_employee(employee: EmployeeCreate, db: AsyncSession = Depends(get_db)):
    """Create a new employee."""
    # Check if telegram_id already exists
    result = await db.execute(select(Employee).where(Employee.telegram_id == employee.telegram_id))
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee with this telegram_id already exists"
        )

    db_employee = Employee(**employee.model_dump())
    db.add(db_employee)
    await db.commit()
    await db.refresh(db_employee)

    return db_employee


@router.put("/{employee_id}", response_model=EmployeeSchema)
async def update_employee(
    employee_id: int,
    employee_update: EmployeeUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update employee."""
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    db_employee = result.scalar_one_or_none()

    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    update_data = employee_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_employee, field, value)

    await db.commit()
    await db.refresh(db_employee)

    return db_employee


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(employee_id: int, db: AsyncSession = Depends(get_db)):
    """Delete employee."""
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    db_employee = result.scalar_one_or_none()

    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    await db.delete(db_employee)
    await db.commit()

    return None


@router.get("/telegram/{telegram_id}", response_model=EmployeeSchema)
async def get_employee_by_telegram(telegram_id: int, db: AsyncSession = Depends(get_db)):
    """Get employee by Telegram ID."""
    result = await db.execute(select(Employee).where(Employee.telegram_id == telegram_id))
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    return employee
