"""
Admin-only routes. Every endpoint here requires is_admin = True.
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..db_models import TaskDB, UserDB
from .. import schemas, auth_schemas
from ..converters import db_to_engine
from ..dependencies import get_current_admin

router = APIRouter()


@router.get("/admin/users", response_model=List[auth_schemas.UserResponse])
def list_all_users(db: Session = Depends(get_db),
                    current_admin: UserDB = Depends(get_current_admin)):
    users = db.query(UserDB).all()
    result = []
    for u in users:
        result.append(auth_schemas.UserResponse(
            id=u.id, username=u.username, is_admin=bool(u.is_admin)
        ))
    return result


@router.get("/admin/tasks", response_model=List[schemas.TaskResponse])
def list_all_tasks(db: Session = Depends(get_db),
                    current_admin: UserDB = Depends(get_current_admin)):
    rows = db.query(TaskDB).all()
    result = []
    for r in rows:
        result.append(db_to_engine(r))
    return result


@router.get("/admin/tasks/by-user/{user_id}", response_model=List[schemas.TaskResponse])
def list_tasks_for_user(user_id: int, db: Session = Depends(get_db),
                         current_admin: UserDB = Depends(get_current_admin)):
    rows = db.query(TaskDB).filter(TaskDB.owner_id == user_id).all()
    result = []
    for r in rows:
        result.append(db_to_engine(r))
    return result