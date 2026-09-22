"""
Module: models/question.py
Mục đích: Biểu diễn Câu hỏi (Question) và Lựa chọn đáp án (QuestionOption).
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

VALID_QUESTION_TYPES = {"multiple_choice", "true_false", "short_answer"}


@dataclass
class Question:
    """Model đại diện cho một câu hỏi kiểm tra."""
    concept_id: int
    content: str
    question_type: str
    id: Optional[int] = None
    explanation: Optional[str] = None
    difficulty: float = 0.5
    points: float = 1.0
    created_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self) -> None:
        if not self.content.strip():
            raise ValueError("Nội dung câu hỏi không được để trống.")
        if self.question_type not in VALID_QUESTION_TYPES:
            raise ValueError(
                f"Loại câu hỏi '{self.question_type}' không hợp lệ. "
                f"Phải thuộc: {VALID_QUESTION_TYPES}"
            )
        if not (0.0 <= self.difficulty <= 1.0):
            raise ValueError(f"Độ khó câu hỏi phải nằm trong [0.0, 1.0], nhận: {self.difficulty}")
        if self.points <= 0.0:
            raise ValueError(f"Điểm số của câu hỏi phải lớn hơn 0.0, nhận: {self.points}")


@dataclass
class QuestionOption:
    """Model đại diện cho phương án lựa chọn của câu hỏi trắc nghiệm."""
    question_id: int
    option_text: str
    option_label: str  # Ví dụ: 'A', 'B', 'C', 'D'
    is_correct: bool = False
    id: Optional[int] = None

    def __post_init__(self) -> None:
        if not self.option_text.strip():
            raise ValueError("Nội dung phương án không được để trống.")
        if not self.option_label.strip():
            raise ValueError("Nhãn phương án (A, B, C...) không được để trống.")