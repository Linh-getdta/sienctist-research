"""
Module: models/test_session.py
Mục đích: Biểu diễn Phiên làm bài kiểm tra (TestSession).
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

VALID_TEST_TYPES = {"standard", "adaptive", "diagnostic"}


@dataclass
class TestSession:
    """Model đại diện cho một phiên làm bài kiểm tra."""
    learner_id: int
    subject_id: int
    test_type: str
    id: Optional[int] = None
    started_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    total_questions: int = 0
    correct_answers: int = 0
    score: float = 0.0

    def __post_init__(self) -> None:
        if self.test_type not in VALID_TEST_TYPES:
            raise ValueError(
                f"Loại bài kiểm tra '{self.test_type}' không hợp lệ. "
                f"Phải thuộc: {VALID_TEST_TYPES}"
            )
        if self.total_questions < 0:
            raise ValueError(f"Tổng số câu hỏi không được âm, nhận: {self.total_questions}")
        if self.correct_answers < 0:
            raise ValueError(f"Số câu trả lời đúng không được âm, nhận: {self.correct_answers}")
        if self.correct_answers > self.total_questions and self.total_questions > 0:
            raise ValueError(
                f"Số câu đúng ({self.correct_answers}) không thể lớn hơn tổng số câu ({self.total_questions})"
            )
        if self.score < 0.0:
            raise ValueError(f"Điểm số không được âm, nhận: {self.score}")