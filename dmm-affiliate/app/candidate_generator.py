from __future__ import annotations

import csv
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import ROOT_DIR, get_settings
from .csv_exporter import write_post_candidates
from .models import PostCandidate, Product
from .post_templates import generate_individual_vr_posts
from .scoring import bucket_item, item_score_detail


DAILY_RULE = {
    "high_commission_individual": 2,
    "cheap_sale_traffic": 1,
    "normal_sale": 1,
}


def _parse_int(value: Any) -> int | None:
    if value is None:
        return None
    text = str(value).strip().replace(",", "").replace("円", "")
    if not text:
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def _parse_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    text = str(value).strip().replace("%", "")
    if not text:
        return default
    try:
        return float(text)
    except ValueError:
        return default


def _is_today_deadline(deadline: str | None) -> bool:
    if not deadline:
        return False
    return deadline in {"今日まで", "本日まで", "本日中", "今日中"} or "今日" in deadline or "本日" in deadline


def _first(row: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return value
    return None


def read_products_csv(source: str | Path) -> list[Product]:
    path = Path(source)
    products: list[Product] = []
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            title = _first(row, "title", "product_name", "商品名")
            if not title:
                continue
            code = _first(row, "product_code", "品番") or str(title)
            products.append(
                Product(
                    product_code=str(code),
                    title=str(title),
                    actress=_first(row, "actress", "女優名"),
                    genre=_first(row, "genre", "ジャンル"),
                    maker=_first(row, "maker", "メーカー"),
                    normal_price=_parse_int(_first(row, "normal_price", "通常価格")),
                    sale_price=_parse_int(_first(row, "sale_price", "セール価格")),
                    review_count=_parse_int(_first(row, "review_count", "レビュー数")) or 0,
                    review_average=_parse_float(_first(row, "review_average", "レビュー平均")),
                    discount_percent=_parse_float(_first(row, "discount_percent", "割引率")),
                    deadline=_first(row, "deadline", "期限"),
                    affiliate_url=_first(row, "affiliate_url", "URL"),
                    content_url=_first(row, "content_url"),
                    image_url=_first(row, "image_url"),
                    raw=row,
                )
            )
    return products


def score_product(product: Product, commission_rate: float = 0.7) -> tuple[dict[str, float], str]:
    detail = item_score_detail(
        review_count=product.review_count,
        review_ave=product.review_average,
        sale_price=product.sale_price,
        commission_rate=commission_rate,
        discount_percent=product.discount_percent,
        is_today_deadline=_is_today_deadline(product.deadline),
    )
    bucket = bucket_item(product.sale_price, float(detail["expected_commission"]))
    return detail, bucket


def ranked_products(products: list[Product]) -> list[tuple[Product, dict[str, float], str]]:
    scored = []
    for product in products:
        detail, bucket = score_product(product)
        scored.append((product, detail, bucket))
    return sorted(scored, key=lambda item: item[1]["total_score"], reverse=True)


def generate_candidates(products: list[Product], limit: int = 5) -> list[PostCandidate]:
    selected: list[tuple[Product, dict[str, float], str]] = []
    bucket_counts: Counter[str] = Counter()

    for product, detail, bucket in ranked_products(products):
        if bucket_counts[bucket] >= DAILY_RULE.get(bucket, 1):
            continue
        bucket_counts[bucket] += 1
        selected.append((product, detail, bucket))
        if len(selected) >= limit:
            break

    if len(selected) < limit:
        used = {product.product_code for product, _detail, _bucket in selected}
        for product, detail, _bucket in ranked_products(products):
            if product.product_code in used:
                continue
            selected.append((product, detail, _bucket))
            if len(selected) >= limit:
                break

    candidates: list[PostCandidate] = []
    for product, detail, _bucket in selected:
        candidates.extend(generate_individual_vr_posts(product, detail))
    return candidates


def generate_candidates_from_csv(
    source: str | Path,
    limit: int = 5,
    output: str | Path | None = None,
) -> tuple[list[PostCandidate], Path]:
    products = read_products_csv(source)
    return generate_candidates_from_products(products=products, limit=limit, output=output)


def generate_candidates_from_supabase(
    limit: int = 5,
    output: str | Path | None = None,
    fetch_limit: int = 300,
    sale_only: bool = True,
    min_discount_percent: float = 0.0,
    require_affiliate_url: bool = True,
) -> tuple[list[PostCandidate], Path]:
    from .supabase_client import fetch_products

    products = fetch_products(
        limit=fetch_limit,
        sale_only=sale_only,
        min_discount_percent=min_discount_percent,
        require_affiliate_url=require_affiliate_url,
    )
    return generate_candidates_from_products(products=products, limit=limit, output=output)


def generate_candidates_from_products(
    products: list[Product],
    limit: int = 5,
    output: str | Path | None = None,
) -> tuple[list[PostCandidate], Path]:
    settings = get_settings()
    candidates = generate_candidates(products, limit=limit)
    output_path = Path(output) if output else ROOT_DIR / "data" / "post_candidates.csv"
    created_at = datetime.now().isoformat(timespec="seconds")
    saved_to = write_post_candidates(
        candidates=candidates,
        output_path=output_path,
        account_id=settings.default_account_id,
        created_at=created_at,
    )
    return candidates, saved_to
