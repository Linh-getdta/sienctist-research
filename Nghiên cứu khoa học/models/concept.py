"""
Module: models/concept.py
Mục đích: Biểu diễn Môn học (Subject), Khái niệm/Chuẩn kiến thức (Concept) 
          và Quan hệ Đồ thị Kiến thức (ConceptRelationship).
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

VALID_RELATIONSHIP_TYPES = {"prerequisite", "related", "depends_on"}


@dataclass
class Subject:
    """Model đại diện cho Môn học."""
    name: str
    id: Optional[int] = None
    description: Optional[str] = None
    created_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Tên môn học không được để trống.")


@dataclass
class Concept:
    """Model đại diện cho một Khái niệm / Chuẩn kiến thức trong môn học."""
    subject_id: int
    name: str
    id: Optional[int] = None
    description: Optional[str] = None
    difficulty: float = 0.5
    created_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Tên khái niệm không được để trống.")
        if not (0.0 <= self.difficulty <= 1.0):
            raise ValueError(f"Độ khó khái niệm phải nằm trong khoảng [0.0, 1.0], nhận: {self.difficulty}")


@dataclass
class ConceptRelationship:
    """Model đại diện cho Cạnh nối (Edge) trong Đồ thị Kiến thức (Knowledge Graph)."""
    source_concept_id: int
    target_concept_id: int
    relationship_type: str
    id: Optional[int] = None
    weight: float = 1.0

    def __post_init__(self) -> None:
        if self.relationship_type not in VALID_RELATIONSHIP_TYPES:
            raise ValueError(
                f"Loại quan hệ '{self.relationship_type}' không hợp lệ. "
                f"Phải thuộc: {VALID_RELATIONSHIP_TYPES}"
            )
        if not (0.0 <= self.weight <= 1.0):
            raise ValueError(f"Trọng số quan hệ weight phải nằm trong khoảng [0.0, 1.0], nhận: {self.weight}")