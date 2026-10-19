import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.core.security import hash_password
from backend.app.models.user import UserDB
from backend.app.schemas.user import UserCreate, UserUpdate, UserResponse
from backend.app.api.deps import get_current_user, require_roles

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: UserDB = Depends(get_current_user)):
    return current_user

@router.get("", response_model=List[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    return db.query(UserDB).all()

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_roles(["admin"]))
):
    existing = db.query(UserDB).filter(UserDB.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un usuario registrado con el correo {user_in.email}"
        )

    user = UserDB(
        id=f"usr-{uuid.uuid4().hex[:8]}",
        name=user_in.name,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        role=user_in.role,
        status="active"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_roles(["admin"]))
):
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    if user_in.name is not None:
        user.name = user_in.name
    if user_in.role is not None:
        user.role = user_in.role
    if user_in.status is not None:
        user.status = user_in.status
    if user_in.password:
        user.hashed_password = hash_password(user_in.password)

    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_roles(["admin"]))
):
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    if user.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No puede eliminar su propia cuenta")

    db.delete(user)
    db.commit()
    return None
