"""
Authentication routes: register, login, forgot password, reset password.
"""

import random
import string
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..db_models import UserDB
from .. import auth_schemas
from ..auth import hash_password, verify_password, create_access_token
from ..email_utils import send_reset_code_email

router = APIRouter()


@router.post("/auth/register", response_model=auth_schemas.UserResponse)
def register(payload: auth_schemas.UserRegister, db: Session = Depends(get_db)):
    existing_username = db.query(UserDB).filter(UserDB.username == payload.username).first()
    if existing_username:
        raise HTTPException(400, "Username already taken")

    existing_email = db.query(UserDB).filter(UserDB.email == payload.email).first()
    if existing_email:
        raise HTTPException(400, "Email already registered")

    is_first_user = db.query(UserDB).count() == 0

    new_user = UserDB(
        username=payload.username,
        email=payload.email,
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


@router.post("/auth/forgot-password")
def forgot_password(payload: auth_schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email == payload.email).first()
    if not user:
        return {"message": "If that email is registered, a reset code has been sent."}

    code = "".join(random.choices(string.digits, k=6))
    expiry = datetime.utcnow() + timedelta(minutes=15)

    user.reset_code = code
    user.reset_code_expiry = expiry.isoformat()
    db.commit()

    try:
        send_reset_code_email(payload.email, code)
    except Exception as e:
        raise HTTPException(500, "Failed to send email: " + str(e))

    return {"message": "If that email is registered, a reset code has been sent."}


@router.post("/auth/reset-password")
def reset_password(payload: auth_schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email == payload.email).first()
    if not user or not user.reset_code:
        raise HTTPException(400, "Invalid or expired reset code")

    if user.reset_code != payload.code:
        raise HTTPException(400, "Invalid or expired reset code")

    expiry = datetime.fromisoformat(user.reset_code_expiry)
    if datetime.utcnow() > expiry:
        raise HTTPException(400, "Reset code has expired - please request a new one")

    user.hashed_password = hash_password(payload.new_password)
    user.reset_code = None
    user.reset_code_expiry = None
    db.commit()

    return {"message": "Password reset successful. You can now log in with your new password."}