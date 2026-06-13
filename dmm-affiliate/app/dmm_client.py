from __future__ import annotations

from typing import Any

from .config import get_settings
from .models import Product


API_ENDPOINT = "https://api.dmm.com/affiliate/v3/ItemList"


def safe_get(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
        if current is None:
            return default
    return current


def _first_name(values: Any) -> str | None:
    if isinstance(values, list) and values:
        first = values[0]
        if isinstance(first, dict):
            return first.get("name")
        return str(first)
    return None


def _parse_price(value: Any) -> int | None:
    if value is None:
        return None
    text = str(value).replace(",", "").replace("円", "").strip()
    if not text:
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def normalize_item(item: dict[str, Any]) -> Product:
    prices = item.get("prices") if isinstance(item.get("prices"), dict) else {}
    review = item.get("review") if isinstance(item.get("review"), dict) else {}
    item_info = item.get("iteminfo") if isinstance(item.get("iteminfo"), dict) else {}

    actresses = safe_get(item_info, "actress", default=[])
    genres = safe_get(item_info, "genre", default=[])
    makers = safe_get(item_info, "maker", default=[])

    return Product(
        product_code=str(item.get("content_id") or item.get("product_id") or item.get("cid") or ""),
        title=str(item.get("title") or ""),
        actress=_first_name(actresses),
        genre=_first_name(genres),
        maker=_first_name(makers),
        normal_price=_parse_price(prices.get("list_price") or prices.get("price")),
        sale_price=_parse_price(prices.get("price")),
        review_count=_parse_price(review.get("count")) or 0,
        review_average=float(review.get("average") or 0),
        affiliate_url=item.get("affiliateURL") or item.get("affiliateUrl"),
        content_url=item.get("URL") or item.get("url"),
        image_url=safe_get(item, "imageURL", "large") or safe_get(item, "imageURL", "small"),
        raw=item,
    )


def fetch_items(
    keyword: str | None = None,
    site: str = "FANZA",
    service: str = "digital",
    floor: str | None = None,
    hits: int = 20,
    offset: int = 1,
    sort: str = "review",
) -> list[Product]:
    settings = get_settings()
    if not settings.dmm_api_id or not settings.dmm_affiliate_id:
        raise RuntimeError("DMM_API_ID and DMM_AFFILIATE_ID are required for fetch-dmm.")

    try:
        import requests
    except ImportError as exc:
        raise RuntimeError("requests is required for fetch-dmm. Run pip install -r requirements.txt.") from exc

    params: dict[str, Any] = {
        "api_id": settings.dmm_api_id,
        "affiliate_id": settings.dmm_affiliate_id,
        "site": site,
        "service": service,
        "hits": hits,
        "offset": offset,
        "sort": sort,
        "output": "json",
    }
    if keyword:
        params["keyword"] = keyword
    if floor:
        params["floor"] = floor

    response = requests.get(API_ENDPOINT, params=params, timeout=20)
    if not response.ok:
        raise RuntimeError(f"DMM API request failed: {response.status_code} {response.text[:300]}")

    payload = response.json()
    items = safe_get(payload, "result", "items", default=[])
    if not isinstance(items, list):
        raise RuntimeError("DMM API response did not contain result.items list.")

    return [normalize_item(item) for item in items if isinstance(item, dict)]
