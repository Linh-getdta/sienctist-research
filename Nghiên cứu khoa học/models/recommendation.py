"""
Module: models/recommendation.py
Mục đích: Biểu diễn Đề xuất học tập cá nhân hóa do AI gợi ý (Recommendation).
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

VALID_RECOMMENDATION_TYPES = {"review", "practice", "advance", "prerequisite"}
VALID_PRIORITIES = {"low", "medium", "high", "critical"}
VALID_STATUSES = {"pending", "accepted", "completed", "dismissed"}


@dataclass
class Recommendation:
    """Model đại diện cho một gợi ý hành động học tập được AI tạo ra."""
    learner_id: int
    concept_id: int
    recommendation_type: str
    id: Optional[int] = None
    priority: str = "medium"
    reason: Optional[str] = None
    confidence: float = 1.0
    created_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "pending"

    def __post_init__(self) -> None:
        if self.recommendation_type not in VALID_RECOMMENDATION_TYPES:
            raise ValueError(
                f"Loại gợi ý '{self.recommendation_type}' không hợp lệ. "
                f"Phải thuộc: {VALID_RECOMMENDATION_TYPES}"
            )
        if self.priority not in VALID_PRIORITIES:
            raise ValueError(
                f"Mức độ ưu tiên '{self.priority}' không hợp lệ. "
                f"Phải thuộc: {VALID_PRIORITIES}"
            )
        if self.status not in VALID_STATUSES:
            raise ValueError(
                f"Trạng thái gợi ý '{self.status}' không hợp lệ. "
                f"Phải thuộc: {VALID_STATUSES}"
            )
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"Độ tin cậy gợi ý phải nằm trong [0.0, 1.0], nhận: {self.confidence}")