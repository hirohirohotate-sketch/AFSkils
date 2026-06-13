from __future__ import annotations

import math
from typing import TypedDict


class ScoreDetail(TypedDict):
    total_score: float
    review_score: float
    commission_score: float
    discount_score: float
    deadline_score: float
    expected_commission: float


def item_score_detail(
    review_count: int,
    review_ave: float,
    sale_price: int | None = None,
    commission_rate: float = 0.7,
    discount_percent: float = 0,
    is_today_deadline: bool = False,
) -> ScoreDetail:
    review_count = max(review_count or 0, 0)
    review_ave = max(review_ave or 0, 0)
    discount_percent = max(discount_percent or 0, 0)

    if review_count <= 0 or review_ave <= 0:
        review_score = 0.0
    else:
        review_score = review_ave * math.log1p(review_count)

    expected_commission = 0.0
    commission_score = 0.0

    if sale_price is not None and sale_price > 0:
        expected_commission = sale_price * commission_rate
        commission_score = expected_commission * 0.02

    discount_score = discount_percent * 0.1
    deadline_score = 2.0 if is_today_deadline else 0.0

    total_score = review_score + commission_score + discount_score + deadline_score

    return {
        "total_score": round(total_score, 4),
        "review_score": round(review_score, 4),
        "commission_score": round(commission_score, 4),
        "discount_score": round(discount_score, 4),
        "deadline_score": round(deadline_score, 4),
        "expected_commission": round(expected_commission, 2),
    }


def bucket_item(sale_price: int | None, expected_commission: float) -> str:
    if sale_price is not None and sale_price <= 150:
        return "cheap_sale_traffic"

    if expected_commission >= 300:
        return "high_commission_individual"

    return "normal_sale"
