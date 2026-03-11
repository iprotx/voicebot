from fastapi import APIRouter, Depends

from backend.api.deps.repositories import get_alert_repo, get_current_admin_email, get_risk_repo
from backend.models.schemas import AlertOut, RiskScoreCreateIn, RiskScoreOut
from backend.services.risk_service import compute_risk_score, risk_level
from backend.storage.repositories import AlertRepository, RiskScoreRepository

router = APIRouter(prefix="/risk", tags=["risk"])


@router.post("/score", response_model=RiskScoreOut)
async def create_risk_score(
    payload: RiskScoreCreateIn,
    _: str = Depends(get_current_admin_email),
    repo: RiskScoreRepository = Depends(get_risk_repo),
    alert_repo: AlertRepository = Depends(get_alert_repo),
) -> RiskScoreOut:
    score = compute_risk_score(payload.style_similarity, payload.activity_overlap, payload.scam_pattern_score)
    level = risk_level(score)
    created = await repo.create(payload, computed_score=score, computed_level=level)
    if score > 70:
        await alert_repo.create_for_risk(created, channels=["dashboard", "telegram", "email"])
    return created


@router.get("/users/{user_id}", response_model=list[RiskScoreOut])
async def get_user_risks(
    user_id: int,
    _: str = Depends(get_current_admin_email),
    repo: RiskScoreRepository = Depends(get_risk_repo),
) -> list[RiskScoreOut]:
    return await repo.list_by_user(user_id)


@router.get("/users/{user_id}/alerts", response_model=list[AlertOut])
async def get_user_alerts(
    user_id: int,
    _: str = Depends(get_current_admin_email),
    repo: AlertRepository = Depends(get_alert_repo),
) -> list[AlertOut]:
    return await repo.list_by_user(user_id)
