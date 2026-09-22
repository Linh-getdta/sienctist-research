"""
Module: models/answer.py
Mục đích: Biểu diễn Lịch sử trả lời (Answer) và Phân tích bản ghi lỗi (ErrorRecord).
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

VALID_ERROR_TYPES = {
    "concept_error",
    "formula_error",
    "calculation_error",
    "careless_error",
    "prerequisite_error",
    "unknown",
}


@dataclass
class Answer:
    """Model đại diện cho câu trả lời của người học trong bài kiểm tra."""
    session_id: int
    question_id: int
    is_correct: bool
    id: Optional[int] = None
    selected_option_id: Optional[int] = None
    answer_text: Optional[str] = None
    response_time: float = 0.0  # Thời gian làm bài tính bằng giây
    answered_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self) -> None:
        if self.response_time < 0.0:
            raise ValueError(f"Thời gian phản hồi không được âm, nhận: {self.response_time}")


@dataclass
class ErrorRecord:
    """Model đại diện cho việc chẩn đoán phân loại nguyên nhân lỗi sai."""
    answer_id: int
    error_type: str = "unknown"
    id: Optional[int] = None
    confidence: float = 1.0
    description: Optional[str] = None
    created_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self) -> None:
        if self.error_type not in VALID_ERROR_TYPES:
            raise ValueError(
                f"Loại lỗi '{self.error_type}' không hợp lệ. "
                f"Phải thuộc: {VALID_ERROR_TYPES}"
            )
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"Độ tin cậy phán đoán lỗi phải trong [0.0, 1.0], nhận: {self.confidence}")