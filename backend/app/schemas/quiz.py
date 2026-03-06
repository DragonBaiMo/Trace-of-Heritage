"""问答相关的 Pydantic 模型。"""
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class QuizQuestionRead(BaseModel):
    """每日题目响应。"""

    id: int
    title: str
    options: List[str]
    active_date: date
    points_reward: int

    class Config:
        orm_mode = True


class QuizAnswerRequest(BaseModel):
    """用户提交答案请求。"""

    question_id: int = Field(..., ge=1, description="题目ID")
    selected_option: str = Field(..., min_length=1, max_length=10, description="所选选项标识")


class QuizAnswerRead(BaseModel):
    """答题结果响应。"""

    question_id: int
    is_correct: bool
    points_reward: int
    message: str
    created_at: datetime
