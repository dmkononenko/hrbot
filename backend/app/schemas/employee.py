from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


class EmployeeBase(BaseModel):
    telegram_id: int = Field(..., description="Telegram user ID")
    telegram_username: Optional[str] = Field(None, max_length=255)
    first_name: Optional[str] = Field(None, max_length=255)
    last_name: Optional[str] = Field(None, max_length=255)
    start_date: date = Field(..., description="Employee start date")
    branch: Optional[str] = Field(None, max_length=255)
    department: Optional[str] = Field(None, max_length=255)
    position: Optional[str] = Field(None, max_length=255)
    gender: Optional[str] = Field(None, max_length=10)
    age: Optional[int] = None
    is_active: bool = True


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    telegram_username: Optional[str] = Field(None, max_length=255)
    first_name: Optional[str] = Field(None, max_length=255)
    last_name: Optional[str] = Field(None, max_length=255)
    start_date: Optional[date] = None
    branch: Optional[str] = Field(None, max_length=255)
    department: Optional[str] = Field(None, max_length=255)
    position: Optional[str] = Field(None, max_length=255)
    gender: Optional[str] = Field(None, max_length=10)
    age: Optional[int] = None
    is_active: Optional[bool] = None


class Employee(EmployeeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmployeeList(BaseModel):
    employees: list[Employee]
    total: int
