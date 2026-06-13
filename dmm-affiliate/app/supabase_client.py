from __future__ import annotations

from datetime import date, datetime
from dataclasses import asdict
from typing import Any

from .config import get_settings
from .models import PostCandidate, Product


def _client():
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_role_key:
        return None

    try:
        from supabase import create_client
    except ImportError as exc:
        raise RuntimeError("supabase package is required when Supabase env vars are set.") from exc

    return create_client(settings.supabase_url, settings.supabase_service_role_key)


def _required_client():
    client = _client()
    if client is None:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required for Supabase reads.")
    return client


def _to_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _to_float(value: Any) -> float:
    if value is None or value == "":
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def product_from_row(row: dict[str, Any]) -> Product:
    normal_price = _to_int(row.get("normal_price"))
    sale_price = _to_int(row.get("sale_price"))
    discount_percent = _to_float(row.get("discount_percent"))
    if discount_percent <= 0 and normal_price and sale_price and normal_price > sale_price:
        discount_percent = round((normal_price - sale_price) / normal_price * 100, 2)

    return Product(
        product_code=str(row.get("product_code") or ""),
        title=str(row.get("title") or ""),
        actress=row.get("actress"),
        genre=row.get("genre"),
        maker=row.get("maker"),
        normal_price=normal_price,
        sale_price=sale_price,
        review_count=_to_int(row.get("review_count")) or 0,
        review_average=_to_float(row.get("review_average")),
        discount_percent=discount_percent,
        deadline=row.get("deadline"),
        affiliate_url=row.get("affiliate_url"),
        content_url=row.get("content_url"),
        image_url=row.get("image_url"),
        raw=row.get("raw_json") or row,
    )


def product_from_work_row(row: dict[str, Any]) -> Product:
    normal_price = _to_int(row.get("normal_price"))
    sale_price = _to_int(row.get("price"))
    discount_percent = _to_float(row.get("discount_rate"))
    if discount_percent <= 0 and normal_price and sale_price and normal_price > sale_price:
        discount_percent = round((normal_price - sale_price) / normal_price * 100, 2)

    actresses = row.get("actresses") or []
    actress = "、".join(actresses[:2]) if isinstance(actresses, list) else str(actresses or "")
    sale_end = row.get("sale_date_end")
    deadline = _format_sale_deadline(sale_end)

    return Product(
        product_code=str(row.get("dmm_id") or row.get("id") or ""),
        title=str(row.get("title") or ""),
        actress=actress or None,
        genre="VR" if row.get("is_vr") else None,
        maker=row.get("maker_name") or row.get("label_name"),
        normal_price=normal_price,
        sale_price=sale_price,
        review_count=_to_int(row.get("review_count")) or 0,
        review_average=_to_float(row.get("review_avg")),
        discount_percent=discount_percent,
        deadline=deadline,
        affiliate_url=row.get("dmm_url"),
        content_url=row.get("dmm_url"),
        image_url=row.get("thumbnail_url"),
        raw=row,
    )


def _format_sale_deadline(value: Any) -> str | None:
    if not value:
        return None
    text = str(value)
    try:
        end_date = datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except ValueError:
        try:
            end_date = datetime.strptime(text[:10], "%Y-%m-%d").date()
        except ValueError:
            return f"{text}まで"

    if end_date == date.today():
        return "本日まで"
    return f"{end_date.month}/{end_date.day}まで"


def fetch_products(
    limit: int = 300,
    sale_only: bool = True,
    min_discount_percent: float = 0.0,
    require_affiliate_url: bool = True,
) -> list[Product]:
    client = _required_client()
    try:
        response = (
            client.table("products")
            .select(
                "product_code,title,actress,genre,maker,normal_price,sale_price,"
                "review_count,review_average,discount_percent,deadline,"
                "affiliate_url,content_url,image_url,raw_json,created_at"
            )
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
    except Exception as exc:
        message = str(exc)
        if "Could not find the table" in message and "products" in message:
            return fetch_works_as_products(
                limit=limit,
                sale_only=sale_only,
                min_discount_percent=min_discount_percent,
                require_affiliate_url=require_affiliate_url,
            )
        raise
    rows = response.data or []
    products = [product_from_row(row) for row in rows if row.get("product_code") and row.get("title")]
    return filter_products(
        products,
        sale_only=sale_only,
        min_discount_percent=min_discount_percent,
        require_affiliate_url=require_affiliate_url,
    )


def fetch_works_as_products(
    limit: int = 300,
    sale_only: bool = True,
    min_discount_percent: float = 0.0,
    require_affiliate_url: bool = True,
) -> list[Product]:
    client = _required_client()
    query = client.table("works").select(
        "id,dmm_id,title,actresses,price,normal_price,discount_rate,is_discount,"
        "dmm_url,thumbnail_url,is_vr,review_avg,review_count,sale_title,"
        "sale_date_begin,sale_date_end,maker_name,label_name,has_ai_analysis,created_at"
    )
    if sale_only:
        query = query.eq("is_discount", True).eq("is_vr", True)
    response = query.order("discount_rate", desc=True).order("review_count", desc=True).limit(limit).execute()
    rows = response.data or []
    products = [product_from_work_row(row) for row in rows if row.get("dmm_id") and row.get("title")]
    return filter_products(
        products,
        sale_only=sale_only,
        min_discount_percent=min_discount_percent,
        require_affiliate_url=require_affiliate_url,
    )


def filter_products(
    products: list[Product],
    sale_only: bool = True,
    min_discount_percent: float = 0.0,
    require_affiliate_url: bool = True,
) -> list[Product]:
    filtered: list[Product] = []
    for product in products:
        if sale_only and not product.sale_price:
            continue
        if sale_only and product.normal_price and product.sale_price >= product.normal_price:
            continue
        if min_discount_percent > 0 and product.discount_percent < min_discount_percent:
            continue
        if require_affiliate_url and not product.affiliate_url:
            continue
        filtered.append(product)
    return filtered


def upsert_products(products: list[Product]) -> None:
    client = _client()
    if client is None:
        return

    rows: list[dict[str, Any]] = []
    for product in products:
        row = asdict(product)
        row["raw_json"] = row.pop("raw", {})
        rows.append(row)
    if rows:
        client.table("products").upsert(rows, on_conflict="product_code").execute()


def insert_post_candidates(candidates: list[PostCandidate]) -> None:
    client = _client()
    if client is None:
        return

    rows = [asdict(candidate) for candidate in candidates]
    if rows:
        client.table("post_candidates").insert(rows).execute()


def insert_sales_reports(rows: list[dict[str, Any]]) -> None:
    client = _client()
    if client is None:
        return

    if rows:
        client.table("sales_reports").insert(rows).execute()
