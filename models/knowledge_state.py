"""
Module: models/knowledge_state.py
Mục đích: Biểu diễn Trạng thái Năng lực Động của Người học (KnowledgeState).
          Model cốt lõi của Knowledge Tracing.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class KnowledgeState:
    """
    Model đại diện cho mức độ nắm vững kiến thức và độ tin cậy của đánh giá
    đối với từng khái niệm cụ thể của người học.
    """
    learner_id: int
    concept_id: int
    id: Optional[int] = None
    mastery: float = 0.0
    confidence: float = 0.0
    attempts: int = 0
    correct_count: int = 0
    incorrect_count: int = 0
    last_updated: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self) -> None:
        if not (0.0 <= self.mastery <= 1.0):
            raise ValueError(f"Mức độ thành thạo (mastery) phải nằm trong [0.0, 1.0], nhận: {self.mastery}")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"Độ tin cậy đánh giá (confidence) phải nằm trong [0.0, 1.0], nhận: {self.confidence}")
        if self.attempts < 0:
            raise ValueError(f"Số lần thử (attempts) không được âm, nhận: {self.attempts}")
        if self.correct_count < 0:
            raise ValueError(f"Số lần đúng không được âm, nhận: {self.correct_count}")
        if self.incorrect_count < 0:
            raise ValueError(f"Số lần sai không được âm, nhận: {self.incorrect_count}")
        if (self.correct_count + self.incorrect_count) > self.attempts:
            raise ValueError(
                f"Tổng số lần đúng ({self.correct_count}) và sai ({self.incorrect_count}) "
                f"không thể vượt quá tổng số lần thử ({self.attempts})"
            )