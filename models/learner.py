"""
Module: models/learner.py
Mục đích: Biểu diễn dữ liệu hồ sơ người học (Learner).
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Learner:
    """
    Model đại diện cho thông tin người học trong hệ thống.
    """
    name: str
    email: str
    id: Optional[int] = None
    age: Optional[int] = None
    learning_goal: Optional[str] = None
    created_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self) -> None:
        if self.age is not None and self.age <= 0:
            raise ValueError(f"Tuổi người học phải lớn hơn 0, nhận giá trị: {self.age}")
        if not self.name.strip():
            raise ValueError("Tên người học không được để trống.")
        if not self.email.strip():
            raise ValueError("Email người học không được để trống.")