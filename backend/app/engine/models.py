"""
Core data structures for the dynamic task scheduling engine.
"""

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import List, Optional


class TaskStatus(str, Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    REPLACED = "replaced"
    COMPLETED = "completed"
    MISSED = "missed"


class TaskCategory(str, Enum):
    URGENT = "urgent"
    ROUTINE = "routine"
    MAINTENANCE = "maintenance"
    PROJECT = "project"
    ADMIN = "admin"


@dataclass
class Task:
    id: str
    name: str
    category: TaskCategory
    deadline: date
    value: float = 0.0
    penalty_if_missed: float = 0.0
    effort_hours: float = 1.0
    budget_required: float = 0.0
    risk: int = 1
    dependencies: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING

    score: float = 0.0
    rank: Optional[int] = None
    score_breakdown: dict = field(default_factory=dict)
    rule_log: List[str] = field(default_factory=list)


@dataclass
class SchedulingContext:
    today: date
    available_hours: float
    available_budget: float