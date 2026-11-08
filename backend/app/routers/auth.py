"""
Authentication & User Profile Router
"""

import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.db.models import User
from backend.app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    Token,
    UpdateDNARequest,
)
from backend.app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
)
from backend.app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["User Authentication & DNA Profile"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(req: UserRegisterRequest, db: Session = Depends(get_db)):
    """Registers a new user and returns an authenticated JWT access token."""
    existing = db.query(User).filter(User.email == req.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists.",
        )

    dna_json = None
    if req.travel_dna:
        dna_json = json.dumps(req.travel_dna.model_dump())

    user = User(
        email=req.email.lower(),
        hashed_password=hash_password(req.password),
        full_name=req.full_name,
        travel_dna_json=dna_json,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(data={"sub": str(user.id), "email": user.email})

    user_resp = UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        travel_dna=json.loads(user.travel_dna_json) if user.travel_dna_json else None,
    )
    return Token(access_token=token, user=user_resp)


@router.post("/login", response_model=Token)
def login(req: UserLoginRequest, db: Session = Depends(get_db)):
    """Authenticates user credentials and returns a JWT access token."""
    user = db.query(User).filter(User.email == req.email.lower()).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(data={"sub": str(user.id), "email": user.email})
    user_resp = UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        travel_dna=json.loads(user.travel_dna_json) if user.travel_dna_json else None,
    )
    return Token(access_token=token, user=user_resp)


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(user: User = Depends(get_current_user)):
    """Returns the authenticated user's profile and calibrated Travel DNA."""
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        travel_dna=json.loads(user.travel_dna_json) if user.travel_dna_json else None,
    )


@router.put("/dna", response_model=UserResponse)
def update_travel_dna(
    req: UpdateDNARequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Updates the user's permanent 7-D Travel DNA psychographic preferences."""
    dna_dict = req.travel_dna.model_dump()
    user.travel_dna_json = json.dumps(dna_dict)
    db.commit()
    db.refresh(user)

    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        travel_dna=dna_dict,
    )

