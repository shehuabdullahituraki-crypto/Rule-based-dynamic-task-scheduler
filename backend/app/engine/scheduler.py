"""
Scheduler module. Contains find_replaceable and reallocate logic.
"""

from typing import List, Tuple
from .models import Task, SchedulingContext, TaskStatus


def _fits(task, hours_left, budget_left):
    return task.effort_hours <= hours_left and task.budget_required <= budget_left


def build_schedule(ranked_tasks: List[Task], context: SchedulingContext) -> Tuple[List[Task], List[Task]]:
    hours_left = context.available_hours
    budget_left = context.available_budget
    scheduled = []
    waitlisted = []

    for task in ranked_tasks:
        if task.status == TaskStatus.MISSED:
            waitlisted.append(task)
            continue
        if _fits(task, hours_left, budget_left):
            task.status = TaskStatus.SCHEDULED
            hours_left = hours_left - task.effort_hours
            budget_left = budget_left - task.budget_required
            scheduled.append(task)
        else:
            task.status = TaskStatus.PENDING
            waitlisted.append(task)

    return scheduled, waitlisted


def find_replaceable(new_task, scheduled, hours_left, budget_left):
    candidates = []
    for t in scheduled:
        if t.score < new_task.score:
            candidates.append(t)
    candidates = sorted(candidates, key=lambda t: t.score)

    freed_hours = hours_left
    freed_budget = budget_left
    to_replace = []
    for task in candidates:
        if freed_hours >= new_task.effort_hours and freed_budget >= new_task.budget_required:
            break
        to_replace.append(task)
        freed_hours = freed_hours + task.effort_hours
        freed_budget = freed_budget + task.budget_required

    if freed_hours >= new_task.effort_hours and freed_budget >= new_task.budget_required:
        return to_replace
    return []


def integrate_new_task(new_task, scheduled, waitlisted, context):
    hours_used = sum(t.effort_hours for t in scheduled)
    budget_used = sum(t.budget_required for t in scheduled)
    hours_left = context.available_hours - hours_used
    budget_left = context.available_budget - budget_used

    report = {"action": None, "replaced": [], "task": new_task.id}

    if _fits(new_task, hours_left, budget_left):
        new_task.status = TaskStatus.SCHEDULED
        scheduled.append(new_task)
        report["action"] = "scheduled_directly"
        return report

    replaceable = find_replaceable(new_task, scheduled, hours_left, budget_left)
    if replaceable:
        for t in replaceable:
            t.status = TaskStatus.REPLACED
            t.rule_log.append("replaced to make room for higher-priority task " + new_task.id)
            scheduled.remove(t)
            waitlisted.append(t)
        new_task.status = TaskStatus.SCHEDULED
        scheduled.append(new_task)
        report["action"] = "replaced_lower_priority"
        report["replaced"] = [t.id for t in replaceable]
        return report

    waitlisted.append(new_task)
    report["action"] = "waitlisted_insufficient_capacity"
    return report