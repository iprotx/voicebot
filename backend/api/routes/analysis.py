from fastapi import APIRouter

from backend.models.schemas import SimilarityRequest, SimilarityResponse
from backend.services.analysis_service import AnalysisService

router = APIRouter(prefix="/analysis", tags=["analysis"])
service = AnalysisService()


@router.post("/similarity", response_model=SimilarityResponse)
async def account_similarity(payload: SimilarityRequest) -> SimilarityResponse:
    result = service.compare_accounts(
        texts_a=payload.account_a.texts,
        timestamps_a=payload.account_a.timestamps,
        texts_b=payload.account_b.texts,
        timestamps_b=payload.account_b.timestamps,
        scam_pattern_score=payload.scam_pattern_score,
    )
    return SimilarityResponse(**result)
