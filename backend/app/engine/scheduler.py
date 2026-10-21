"""
Scheduler module - day-bucketed scheduling (Monday-Friday), each day
with its own free-hours capacity. When a day is full and a new,
higher-priority task needs room, the engine first tries COMPRESSING
the lowest-priority task(s) already on that day (reducing their
allocated hours down to a minimum floor) before falling back to a
full replacement (removing a task from that day entirely).
"""

from typing import List, Dict, Tuple
from .models import Task, SchedulingContext, TaskStatus

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
MIN_EFFORT_HOURS = 0.5  # a task can never be compressed below this


def _weekday_name(task: Task) -> str:
    name = task.deadline.strftime("%A")
    return name if name in WEEKDAYS else "Monday"  # weekend deadlines fold into Monday


def _remove_duplicate_tasks(tasks: List[Task]) -> List[Task]:
    """If the same task name appears more than once, keep only the
    highest-scoring instance and drop the rest."""
    best_by_name = {}
    for t in tasks:
        if t.name not in best_by_name or t.score > best_by_name[t.name].score:
            best_by_name[t.name] = t

    kept_ids = {t.id for t in best_by_name.values()}
    for t in tasks:
        if t.id not in kept_ids:
            t.status = TaskStatus.REPLACED
            t.rule_log.append("removed as a duplicate of a higher-scoring task with the same name")

    return [t for t in tasks if t.id in kept_ids]


def build_schedule(ranked_tasks: List[Task],
                    context: SchedulingContext) -> Tuple[List[Task], List[Task]]:
    tasks = _remove_duplicate_tasks(ranked_tasks)
    duplicates_removed = [t for t in ranked_tasks if t not in tasks]

    daily_hours_left: Dict[str, float] = {d: context.available_hours for d in WEEKDAYS}
    budget_left = context.available_budget

    scheduled, waitlisted = [], []

    for task in tasks:
        if task.status == TaskStatus.MISSED:
            waitlisted.append(task)
            continue

        day = _weekday_name(task)
        hours_left = daily_hours_left[day]

        if task.effort_hours <= hours_left and task.budget_required <= budget_left:
            task.status = TaskStatus.SCHEDULED
            daily_hours_left[day] -= task.effort_hours
            budget_left -= task.budget_required
            scheduled.append(task)
        else:
            task.status = TaskStatus.PENDING
            waitlisted.append(task)

    return scheduled, waitlisted + duplicates_removed


def _compress_for_room(day: str, needed_hours: float, scheduled: List[Task],
                        new_task_score: float) -> float:
    """Shrinks lower-scoring tasks on the given day (down to MIN_EFFORT_HOURS)
    to free up capacity. Returns hours actually freed."""
    candidates = sorted(
        [t for t in scheduled if _weekday_name(t) == day and t.score < new_task_score],
        key=lambda t: t.score,
    )

    freed = 0.0
    for t in candidates:
        if freed >= needed_hours:
            break
        compressible = t.effort_hours - MIN_EFFORT_HOURS
        if compressible <= 0:
            continue
        amount = min(compressible, needed_hours - freed)
        t.effort_hours -= amount
        t.rule_log.append(f"compressed by {amount:.2f}h to make room for a higher-priority task")
        freed += amount

    return freed


def find_replaceable(day: str, new_task: Task, scheduled: List[Task],
                      hours_left: float, budget_left: float) -> List[Task]:
    candidates = sorted(
        [t for t in scheduled if _weekday_name(t) == day and t.score < new_task.score],
        key=lambda t: t.score,
    )

    freed_hours, freed_budget = hours_left, budget_left
    to_replace = []
    for task in candidates:
        if freed_hours >= new_task.effort_hours and freed_budget >= new_task.budget_required:
            break
        to_replace.append(task)
        freed_hours += task.effort_hours
        freed_budget += task.budget_required

    if freed_hours >= new_task.effort_hours and freed_budget >= new_task.budget_required:
        return to_replace
    return []


def integrate_new_task(new_task: Task, scheduled: List[Task], waitlisted: List[Task],
                        context: SchedulingContext) -> dict:
    day = _weekday_name(new_task)

    hours_used = sum(t.effort_hours for t in scheduled if _weekday_name(t) == day)
    budget_used = sum(t.budget_required for t in scheduled)
    hours_left = context.available_hours - hours_used
    budget_left = context.available_budget - budget_used

    report = {"action": None, "compressed": [], "replaced": [], "task": new_task.id, "day": day}

    if new_task.effort_hours <= hours_left and new_task.budget_required <= budget_left:
        new_task.status = TaskStatus.SCHEDULED
        scheduled.append(new_task)
        report["action"] = "scheduled_directly"
        return report

    # Step 1: try compressing lower-priority tasks on the same day
    needed = new_task.effort_hours - hours_left
    if needed > 0:
        before = [(t.id, t.effort_hours) for t in scheduled if _weekday_name(t) == day]
        freed = _compress_for_room(day, needed, scheduled, new_task.score)
        hours_left += freed
        compressed_ids = [t_id for (t_id, before_hours) in before
                           for t in scheduled if t.id == t_id and t.effort_hours < before_hours]
        report["compressed"] = compressed_ids

    if new_task.effort_hours <= hours_left and new_task.budget_required <= budget_left:
        new_task.status = TaskStatus.SCHEDULED
        scheduled.append(new_task)
        report["action"] = "scheduled_after_compression" if report["compressed"] else "scheduled_directly"
        return report

    # Step 2: compression wasn't enough - fall back to full replacement
    replaceable = find_replaceable(day, new_task, scheduled, hours_left, budget_left)
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