"""
Pydantic schemas - define what the API accepts (requests) and returns (responses).
"""

from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    id: str
    name: str
    category: str = Field(description="urgent, routine, maintenance, project, admin, or any custom label")
    deadline: date
    value: float = 0.0
    penalty_if_missed: float = 0.0
    effort_hours: float = 1.0
    budget_required: float = 0.0
    risk: int = 1
    dependencies: List[str] = []


class TaskResponse(BaseModel):
    id: str
    name: str
    category: str
    deadline: date
    value: float
    penalty_if_missed: float
    effort_hours: float
    budget_required: float
    risk: int
    dependencies: List[str]
    status: str
    score: float
    rank: Optional[int] = None
    rule_log: List[str] = []

    class Config:
        from_attributes = True


class ScheduleContextIn(BaseModel):
    today: Optional[date] = None
    available_hours: float
    available_budget: float


class ScheduleResult(BaseModel):
    ranked: List[TaskResponse]
    scheduled: List[TaskResponse]
    waitlisted: List[TaskResponse]


class DynamicAddRequest(BaseModel):
    new_task: TaskCreate
    context: ScheduleContextIn