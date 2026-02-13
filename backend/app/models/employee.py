from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    telegram_username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    start_date = Column(Date, nullable=False, index=True)
    branch = Column(String(255))
    department = Column(String(255))
    position = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    responses = relationship("SurveyResponse", back_populates="employee", cascade="all, delete-orphan")
