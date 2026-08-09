"""
API routes for tasks and scheduling.
All endpoints require a logged-in user. Tasks are scoped to the
current user - no one can see or modify another user's tasks.
"""

from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..db_models import TaskDB, UserDB
from .. import schemas
from ..converters import db_to_engine, engine_to_db
from ..engine.models import Task, TaskCategory, SchedulingContext
from ..engine.engine import run_full_cycle, add_task_dynamically
from ..dependencies import get_current_user

router = APIRouter()


def _category_or_default(value):
    if value in TaskCategory._value2member_map_:
        return TaskCategory(value)
    return TaskCategory.ADMIN


@router.post("/tasks", response_model=schemas.TaskResponse)
def create_task(payload: schemas.TaskCreate, db: Session = Depends(get_db),
                 current_user: UserDB = Depends(get_current_user)):
    existing = db.query(TaskDB).filter(
        TaskDB.id == payload.id, TaskDB.owner_id == current_user.id
    ).first()
    if existing:
        raise HTTPException(400, "You already have a task with id '" + payload.id + "'")

    engine_task = Task(
        id=payload.id,
        name=payload.name,
        category=_category_or_default(payload.category),
        deadline=payload.deadline,
        value=payload.value,
        penalty_if_missed=payload.penalty_if_missed,
        effort_hours=payload.effort_hours,
        budget_required=payload.budget_required,
        risk=payload.risk,
        dependencies=payload.dependencies,
    )
    row = engine_to_db(engine_task)
    row.owner_id = current_user.id
    db.add(row)
    db.commit()
    db.refresh(row)
    return db_to_engine(row)


@router.get("/tasks", response_model=List[schemas.TaskResponse])
def list_tasks(db: Session = Depends(get_db),
               current_user: UserDB = Depends(get_current_user)):
    rows = db.query(TaskDB).filter(TaskDB.owner_id == current_user.id).all()
    result = []
    for r in rows:
        result.append(db_to_engine(r))
    return result


@router.delete("/tasks/{task_id}")
def delete_task(task_id: str, db: Session = Depends(get_db),
                 current_user: UserDB = Depends(get_current_user)):
    row = db.query(TaskDB).filter(
        TaskDB.id == task_id, TaskDB.owner_id == current_user.id
    ).first()
    if not row:
        raise HTTPException(404, "Task not found")
    db.delete(row)
    db.commit()
    return {"deleted": task_id}


@router.post("/schedule/run", response_model=schemas.ScheduleResult)
def run_schedule(payload: schemas.ScheduleContextIn, db: Session = Depends(get_db),
                  current_user: UserDB = Depends(get_current_user)):
    rows = db.query(TaskDB).filter(TaskDB.owner_id == current_user.id).all()
    tasks = []
    for r in rows:
        tasks.append(db_to_engine(r))
    if not tasks:
        raise HTTPException(400, "No tasks in the system yet - create some first")

    if payload.today:
        context_today = payload.today
    else:
        context_today = date.today()

    context = SchedulingContext(
        today=context_today,
        available_hours=payload.available_hours,
        available_budget=payload.available_budget,
    )
    result = run_full_cycle(tasks, context)

    row_map = {}
    for r in rows:
        row_map[r.id] = r

    for t in result["ranked"]:
        engine_to_db(t, row_map[t.id])
    db.commit()

    return result


@router.post("/schedule/dynamic-add", response_model=dict)
def dynamic_add(payload: schemas.DynamicAddRequest, db: Session = Depends(get_db),
                 current_user: UserDB = Depends(get_current_user)):
    rows = db.query(TaskDB).filter(TaskDB.owner_id == current_user.id).all()
    all_tasks = []
    for r in rows:
        all_tasks.append(db_to_engine(r))

    row_map = {}
    for r in rows:
        row_map[r.id] = r

    p = payload.new_task

    if p.id in row_map:
        raise HTTPException(400, "You already have a task with id '" + p.id + "'")

    if payload.context.today:
        context_today = payload.context.today
    else:
        context_today = date.today()

    context = SchedulingContext(
        today=context_today,
        available_hours=payload.context.available_hours,
        available_budget=payload.context.available_budget,
    )

    scheduled = []
    waitlisted = []
    for t in all_tasks:
        if t.status.value == "scheduled":
            scheduled.append(t)
        else:
            waitlisted.append(t)

    new_task = Task(
        id=p.id,
        name=p.name,
        category=_category_or_default(p.category),
        deadline=p.deadline,
        value=p.value,
        penalty_if_missed=p.penalty_if_missed,
        effort_hours=p.effort_hours,
        budget_required=p.budget_required,
        risk=p.risk,
        dependencies=p.dependencies,
    )

    report = add_task_dynamically(new_task, all_tasks, scheduled, waitlisted, context)

    new_row = engine_to_db(new_task)
    new_row.owner_id = current_user.id
    db.add(new_row)
    for t in scheduled + waitlisted:
        if t.id in row_map:
            engine_to_db(t, row_map[t.id])
    db.commit()

    return report