"""AI 能力相关接口。"""
from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user, require_roles
from app.localization.messages import MESSAGES
from app.schemas.ai import AISynopsisRequest, AISynopsisResponse
from app.schemas.common import ResponseModel
from app.services.ai_service import AIService
from app.utils.exceptions import BusinessException

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/synopsis", dependencies=[Depends(require_roles("practitioner", "admin"))], response_model=ResponseModel[AISynopsisResponse])
def generate_synopsis(payload: AISynopsisRequest, _=Depends(get_current_user)) -> ResponseModel[AISynopsisResponse]:
    """调用大模型生成简介与标签。"""

    service = AIService()
    try:
        synopsis, tags = service.generate_synopsis_and_tags(payload.content, payload.expect_length)
    except BusinessException as exc:
        raise HTTPException(status_code=400, detail=exc.message) from exc
    return ResponseModel(code=0, message=MESSAGES["ai_generated"], data=AISynopsisResponse(synopsis=synopsis, tags=tags))
