"""
Orchestrator: chains SCORE -> RULES -> RANK -> SCHEDULE together.
"""

from typing import List
from .models import Task, SchedulingContext
from .scorer import score_tasks
from .rules import apply_rules
from .ranker import rank_tasks
from .scheduler import build_schedule, integrate_new_task


def run_full_cycle(tasks: List[Task], context: SchedulingContext) -> dict:
    task_map = {}
    for t in tasks:
        task_map[t.id] = t

    score_tasks(tasks, context)
    apply_rules(tasks, context, task_map=task_map)
    ranked = rank_tasks(tasks)
    scheduled, waitlisted = build_schedule(ranked, context)

    return {
        "ranked": ranked,
        "scheduled": scheduled,
        "waitlisted": waitlisted,
    }


def add_task_dynamically(new_task, tasks, scheduled, waitlisted, context):
    all_tasks = tasks + [new_task]
    task_map = {}
    for t in all_tasks:
        task_map[t.id] = t

    score_tasks(all_tasks, context)
    apply_rules(all_tasks, context, task_map=task_map)
    rank_tasks(all_tasks)

    report = integrate_new_task(new_task, scheduled, waitlisted, context)
    rank_tasks(scheduled + waitlisted)
    return report