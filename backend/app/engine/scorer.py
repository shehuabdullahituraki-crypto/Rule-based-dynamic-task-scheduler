"""
Scoring module. Converts task attributes into a single 0-1 priority score.
"""

from datetime import date
from typing import List

from .models import Task, SchedulingContext

DEFAULT_WEIGHTS = {
    "urgency": 0.35,
    "value_impact": 0.35,
    "risk": 0.20,
    "effort_bonus": 0.10,
}


def _normalize(value, min_v, max_v):
    if max_v == min_v:
        return 0.5
    result = (value - min_v) / (max_v - min_v)
    if result < 0.0:
        return 0.0
    if result > 1.0:
        return 1.0
    return result


def _urgency(task, today):
    days_left = (task.deadline - today).days
    if days_left <= 0:
        return 1.0
    urgency = 1.0 - (days_left / 5.0)
    if urgency < 0.0:
        return 0.0
    return urgency


def score_tasks(tasks: List[Task], context: SchedulingContext, weights: dict = None) -> List[Task]:
    if weights is None:
        weights = DEFAULT_WEIGHTS
    if not tasks:
        return tasks

    value_values = [t.value + t.penalty_if_missed for t in tasks]
    effort_values = [t.effort_hours + t.budget_required for t in tasks]
    v_min = min(value_values)
    v_max = max(value_values)
    e_min = min(effort_values)
    e_max = max(effort_values)

    for task in tasks:
        urgency = _urgency(task, context.today)
        value_impact = _normalize(task.value + task.penalty_if_missed, v_min, v_max)
        risk = task.risk / 5.0
        effort_bonus = 1.0 - _normalize(task.effort_hours + task.budget_required, e_min, e_max)

        breakdown = {
            "urgency": round(urgency, 3),
            "value_impact": round(value_impact, 3),
            "risk": round(risk, 3),
            "effort_bonus": round(effort_bonus, 3),
        }

        score = (
            weights["urgency"] * urgency
            + weights["value_impact"] * value_impact
            + weights["risk"] * risk
            + weights["effort_bonus"] * effort_bonus
        )

        task.score = round(score, 4)
        task.score_breakdown = breakdown

    return tasks