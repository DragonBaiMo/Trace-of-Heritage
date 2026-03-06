"""每日问答服务。"""
from __future__ import annotations

from datetime import date, datetime
from typing import List

from sqlalchemy.orm import Session

from app.models.quiz import QuizQuestion, QuizUserAnswer
from app.utils.exceptions import BusinessException


class QuizService:
    """处理每日一题的读取与作答逻辑。"""

    def __init__(self, db: Session):
        self.db = db

    def get_today_question(self) -> QuizQuestion:
        """获取当日题目，若不存在则自动生成内置题库的默认题。"""

        today = date.today()
        question = (
            self.db.query(QuizQuestion)
            .filter(QuizQuestion.active_date == today)
            .first()
        )
        if question:
            return question
        return self._create_default_question(today)

    def answer(self, *, question_id: int, user_id: int, selected_option: str) -> tuple[QuizUserAnswer, bool, int]:
        """提交答案，返回记录、是否正确与奖励积分。"""

        question = self.db.query(QuizQuestion).filter(QuizQuestion.id == question_id).first()
        if not question:
            raise BusinessException("题目不存在")

        existed = (
            self.db.query(QuizUserAnswer)
            .filter(
                QuizUserAnswer.question_id == question_id,
                QuizUserAnswer.user_id == user_id,
            )
            .first()
        )
        if existed:
            raise BusinessException("今日已作答，请明日再试")

        is_correct = selected_option.strip().upper() == question.correct_option.upper()
        record = QuizUserAnswer(
            user_id=user_id,
            question_id=question_id,
            selected_option=selected_option.upper(),
            is_correct=is_correct,
        )
        reward_points = question.points_reward if is_correct else 0

        self.db.add(record)
        if reward_points > 0:
            from app.services.product_service import ProductService

            point_service = ProductService(self.db)
            points = point_service.ensure_points_row(user_id)
            points.balance += reward_points
            self.db.add(points)
        self.db.commit()
        self.db.refresh(record)
        return record, is_correct, reward_points

    def _create_default_question(self, target_date: date) -> QuizQuestion:
        """当日无题时创建默认题库中的一道题。"""

        seeds = [
            {
                "title": "以下哪一项是中国四大名旦之一？",
                "options": ["A. 梅兰芳", "B. 周恩来", "C. 鲁迅", "D. 李白"],
                "answer": "A",
            },
            {
                "title": "昆曲的发源地是哪里？",
                "options": ["A. 北京", "B. 苏州", "C. 西安", "D. 成都"],
                "answer": "B",
            },
            {
                "title": "皮影戏的主要表现形式是？",
                "options": ["A. 歌唱", "B. 舞蹈", "C. 光影投射", "D. 杂技"],
                "answer": "C",
            },
        ]
        idx = target_date.toordinal() % len(seeds)
        chosen = seeds[idx]
        question = QuizQuestion(
            title=chosen["title"],
            options="|".join(chosen["options"]),
            correct_option=chosen["answer"],
            active_date=target_date,
            points_reward=5,
        )
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question

    @staticmethod
    def unpack_options(question: QuizQuestion) -> List[str]:
        """将存储的选项字符串转换为列表。"""

        return [opt for opt in (question.options or "").split("|") if opt]
