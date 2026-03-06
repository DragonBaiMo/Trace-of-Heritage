"""每日一题接口。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_session
from app.localization.messages import MESSAGES
from app.models.user import User
from app.schemas.common import ResponseModel
from app.schemas.quiz import QuizAnswerRead, QuizAnswerRequest, QuizQuestionRead
from app.services.quiz_service import QuizService
from app.utils.exceptions import BusinessException

router = APIRouter(prefix="/quiz", tags=["问答"])


@router.get("/today", response_model=ResponseModel[QuizQuestionRead])
def get_today_question(current_user: User = Depends(get_current_user), db: Session = Depends(get_db_session)) -> ResponseModel[QuizQuestionRead]:
    """返回今日题目。"""

    service = QuizService(db)
    question = service.get_today_question()
    return ResponseModel(
        code=0,
        message=MESSAGES["quiz_loaded"],
        data=QuizQuestionRead(
            id=question.id,
            title=question.title,
            options=QuizService.unpack_options(question),
            active_date=question.active_date,
            points_reward=question.points_reward,
        ),
    )


@router.post("/answer", response_model=ResponseModel[QuizAnswerRead])
def answer_question(
    payload: QuizAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> ResponseModel[QuizAnswerRead]:
    """提交题目答案。"""

    service = QuizService(db)
    try:
        record, is_correct, reward = service.answer(
            question_id=payload.question_id,
            user_id=current_user.id,
            selected_option=payload.selected_option,
        )
    except BusinessException as exc:
        raise HTTPException(status_code=400, detail=exc.message) from exc

    msg = "回答正确，积分已发放" if is_correct else "回答错误，欢迎明日继续挑战"
    return ResponseModel(
        code=0,
        message=MESSAGES["quiz_answered"],
        data=QuizAnswerRead(
            question_id=record.question_id,
            is_correct=is_correct,
            points_reward=reward,
            message=msg,
            created_at=record.created_at,
        ),
    )
