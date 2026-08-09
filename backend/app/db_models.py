"""
SQLAlchemy ORM models - Task and User tables.
"""

from sqlalchemy import Column, String, Float, Integer, Date, Text
from .database import Base


class TaskDB(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    owner_id = Column(Integer, nullable=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    deadline = Column(Date, nullable=False)

    value = Column(Float, default=0.0)
    penalty_if_missed = Column(Float, default=0.0)
    effort_hours = Column(Float, default=1.0)
    budget_required = Column(Float, default=0.0)
    risk = Column(Integer, default=1)

    dependencies = Column(Text, default="")
    status = Column(String, default="pending")

    score = Column(Float, default=0.0)
    rank = Column(Integer, nullable=True)
    rule_log = Column(Text, default="")


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Integer, default=0)