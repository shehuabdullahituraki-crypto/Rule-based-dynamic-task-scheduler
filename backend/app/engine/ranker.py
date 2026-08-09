"""
Ranking module. Sorts tasks by score, blocked/missed tasks sink to bottom.
"""

from typing import List
from .models import Task, TaskStatus


def rank_tasks(tasks: List[Task]) -> List[Task]:
    def sort_key(t):
        blocked = t.status == TaskStatus.MISSED or "blocked" in " ".join(t.rule_log)
        return (blocked, -t.score)

    ordered = sorted(tasks, key=sort_key)
    rank_number = 1
    for task in ordered:
        task.rank = rank_number
        rank_number = rank_number + 1
    return ordered