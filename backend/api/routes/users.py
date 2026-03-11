from fastapi import APIRouter, Depends, HTTPException

from backend.api.deps.repositories import get_user_repo
from backend.models.schemas import UserIn, UserOut
from backend.storage.repositories import UserRepository

router = APIRouter()


@router.post("", response_model=UserOut)
async def upsert_user(payload: UserIn, repo: UserRepository = Depends(get_user_repo)) -> UserOut:
    return await repo.upsert(payload)


@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: int, repo: UserRepository = Depends(get_user_repo)) -> UserOut:
    user = await repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    return user
