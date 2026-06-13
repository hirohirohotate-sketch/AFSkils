from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Product:
    product_code: str
    title: str
    actress: str | None = None
    genre: str | None = None
    maker: str | None = None
    normal_price: int | None = None
    sale_price: int | None = None
    review_count: int = 0
    review_average: float = 0.0
    discount_percent: float = 0.0
    deadline: str | None = None
    affiliate_url: str | None = None
    content_url: str | None = None
    image_url: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class PostCandidate:
    product_code: str
    product_name: str
    actress: str | None
    genre: str | None
    template_type: str
    variant: str
    experiment_id: str
    post_text: str
    normal_price: int | None
    sale_price: int | None
    deadline: str | None
    reward_type: str
    affiliate_url: str
    score: float
    score_detail: dict[str, Any]
    bucket: str
    notes: str = ""
