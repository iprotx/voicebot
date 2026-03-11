from fastapi import APIRouter, Depends, HTTPException

from backend.api.deps.repositories import get_current_admin_email, get_integration_repo
from backend.models.schemas import IntegrationIn, IntegrationOut
from backend.storage.repositories import IntegrationRepository

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("", response_model=list[IntegrationOut])
async def list_integrations(
    _: str = Depends(get_current_admin_email),
    repo: IntegrationRepository = Depends(get_integration_repo),
) -> list[IntegrationOut]:
    return await repo.list_all()


@router.post("", response_model=IntegrationOut)
async def create_integration(
    payload: IntegrationIn,
    _: str = Depends(get_current_admin_email),
    repo: IntegrationRepository = Depends(get_integration_repo),
) -> IntegrationOut:
    return await repo.create(payload)


@router.patch("/{integration_id}/activate", response_model=IntegrationOut)
async def activate_integration(
    integration_id: int,
    _: str = Depends(get_current_admin_email),
    repo: IntegrationRepository = Depends(get_integration_repo),
) -> IntegrationOut:
    item = await repo.set_active(integration_id, True)
    if not item:
        raise HTTPException(status_code=404, detail="integration not found")
    return item


@router.patch("/{integration_id}/deactivate", response_model=IntegrationOut)
async def deactivate_integration(
    integration_id: int,
    _: str = Depends(get_current_admin_email),
    repo: IntegrationRepository = Depends(get_integration_repo),
) -> IntegrationOut:
    item = await repo.set_active(integration_id, False)
    if not item:
        raise HTTPException(status_code=404, detail="integration not found")
    return item
