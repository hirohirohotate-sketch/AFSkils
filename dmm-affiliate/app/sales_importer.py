from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


SALES_FIELDS = [
    "sold_at",
    "product_code",
    "product_title",
    "sale_price",
    "commission_type",
    "commission_count",
    "commission_yen",
]


def _read_text(path: Path) -> str:
    for encoding in ("utf-8-sig", "cp932"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def _first(row: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return value
    return ""


def _int(value: Any) -> int | str:
    text = str(value).replace(",", "").replace("円", "").strip()
    if not text:
        return ""
    try:
        return int(float(text))
    except ValueError:
        return ""


def normalize_sales_rows(source: str | Path) -> list[dict[str, Any]]:
    path = Path(source)
    text = _read_text(path)
    rows: list[dict[str, Any]] = []
    reader = csv.DictReader(text.splitlines())
    for row in reader:
        product_title = _first(row, "product_title", "商品タイトル", "商品名")
        if not product_title:
            continue
        rows.append(
            {
                "sold_at": _first(row, "sold_at", "date", "日付"),
                "product_code": _first(row, "product_code", "品番"),
                "product_title": product_title,
                "sale_price": _int(_first(row, "sale_price", "販売金額")),
                "commission_type": _first(row, "commission_type", "報酬体系"),
                "commission_count": _int(_first(row, "commission_count", "報酬件数")),
                "commission_yen": _int(_first(row, "commission_yen", "報酬額")),
            }
        )
    return rows


def write_sales_csv(rows: list[dict[str, Any]], output: str | Path) -> Path:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SALES_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return path


def import_sales(source: str | Path, output: str | Path) -> tuple[list[dict[str, Any]], Path]:
    rows = normalize_sales_rows(source)
    return rows, write_sales_csv(rows, output)
