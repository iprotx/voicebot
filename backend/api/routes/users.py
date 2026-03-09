from fastapi import APIRouter, HTTPException

from backend.api.deps.repositories import user_repo
from backend.models.schemas import UserIn, UserOut

router = APIRouter()


@router.post("", response_model=UserOut)
def upsert_user(payload: UserIn) -> UserOut:
    return user_repo.upsert(payload)


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int) -> UserOut:
    user = user_repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    return user
