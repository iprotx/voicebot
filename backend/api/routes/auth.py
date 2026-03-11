from fastapi import APIRouter, Depends, HTTPException

from backend.api.deps.repositories import get_admin_repo
from backend.models.schemas import AdminLoginIn, AdminRegisterIn, TokenOut
from backend.services.security_service import create_access_token, hash_password, verify_password
from backend.storage.repositories import AdminRepository

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut)
async def register_admin(payload: AdminRegisterIn, repo: AdminRepository = Depends(get_admin_repo)) -> TokenOut:
    existing = await repo.get_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=409, detail="admin already exists")

    await repo.create(payload.email, hash_password(payload.password))
    return TokenOut(access_token=create_access_token(payload.email))


@router.post("/login", response_model=TokenOut)
async def login_admin(payload: AdminLoginIn, repo: AdminRepository = Depends(get_admin_repo)) -> TokenOut:
    admin = await repo.get_by_email(payload.email)
    if not admin or not verify_password(payload.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="invalid credentials")
    return TokenOut(access_token=create_access_token(payload.email))
