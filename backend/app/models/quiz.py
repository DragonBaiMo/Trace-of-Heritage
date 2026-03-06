"""每日问答领域模型。"""
from datetime import date, datetime

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base


class QuizQuestion(Base):
    """每日一题的题干与正确答案。"""

    __tablename__ = "quiz_questions"
    __table_args__ = (UniqueConstraint("active_date", name="uq_quiz_active_date"),)

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    options = Column(String(1000), nullable=False)  # 使用分号分隔的选项文本
    correct_option = Column(String(10), nullable=False)
    active_date = Column(Date, nullable=False, default=date.today)
    points_reward = Column(Integer, nullable=False, default=5)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    answers = relationship("QuizUserAnswer", back_populates="question", cascade="all, delete-orphan")


class QuizUserAnswer(Base):
    """用户答题记录。"""

    __tablename__ = "quiz_user_answers"
    __table_args__ = (UniqueConstraint("user_id", "question_id", name="uq_quiz_user_answer"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("quiz_questions.id"), nullable=False)
    selected_option = Column(String(10), nullable=False)
    is_correct = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    question = relationship("QuizQuestion", back_populates="answers")
