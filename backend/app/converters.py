"""
Converters between the DB row (TaskDB) and the engine dataclass (Task).
"""

from .db_models import TaskDB
from .engine.models import Task, TaskCategory, TaskStatus


def db_to_engine(row):
    deps = []
    for d in (row.dependencies or "").split(","):
        if d:
            deps.append(d)

    if row.category in TaskCategory._value2member_map_:
        category = TaskCategory(row.category)
    else:
        category = TaskCategory.ADMIN

    log_lines = []
    for l in (row.rule_log or "").split("\n"):
        if l:
            log_lines.append(l)

    return Task(
        id=row.id,
        name=row.name,
        category=category,
        deadline=row.deadline,
        value=row.value,
        penalty_if_missed=row.penalty_if_missed,
        effort_hours=row.effort_hours,
        budget_required=row.budget_required,
        risk=row.risk,
        dependencies=deps,
        status=TaskStatus(row.status),
        score=row.score,
        rank=row.rank,
        rule_log=log_lines,
    )


def engine_to_db(task, row=None):
    if row is None:
        row = TaskDB(id=task.id)

    row.name = task.name
    row.category = task.category.value
    row.deadline = task.deadline
    row.value = task.value
    row.penalty_if_missed = task.penalty_if_missed
    row.effort_hours = task.effort_hours
    row.budget_required = task.budget_required
    row.risk = task.risk
    row.dependencies = ",".join(task.dependencies)
    row.status = task.status.value
    row.score = task.score
    row.rank = task.rank
    row.rule_log = "\n".join(task.rule_log)
    return row