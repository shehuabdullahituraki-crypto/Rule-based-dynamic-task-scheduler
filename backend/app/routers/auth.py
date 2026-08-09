"""
Authentication routes: register and login.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..db_models import UserDB
from .. import auth_schemas
from ..auth import hash_password, verify_password, create_access_token

router = APIRouter()


@router.post("/auth/register", response_model=auth_schemas.UserResponse)
def register(payload: auth_schemas.UserRegister, db: Session = Depends(get_db)):
    existing = db.query(UserDB).filter(UserDB.username == payload.username).first()
    if existing:
        raise HTTPException(400, "Username already taken")

    is_first_user = db.query(UserDB).count() == 0

    new_user = UserDB(
        username=payload.username,
        hashed_password=hash_password(payload.password),
        is_admin=1 if is_first_user else 0,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return auth_schemas.UserResponse(
        id=new_user.id,
        username=new_user.username,
        is_admin=bool(new_user.is_admin),
    )


@router.post("/auth/login", response_model=auth_schemas.TokenResponse)
def login(payload: auth_schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.username == payload.username).first()
    if not user:
        raise HTTPException(401, "Incorrect username or password")

    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(401, "Incorrect username or password")

    token = create_access_token({"user_id": user.id, "username": user.username})

    return auth_schemas.TokenResponse(
        access_token=token,
        token_type="bearer",
        user=auth_schemas.UserResponse(
            id=user.id,
            username=user.username,
            is_admin=bool(user.is_admin),
        ),
    )