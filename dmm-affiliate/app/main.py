from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from .candidate_generator import (
    generate_candidates_from_csv,
    generate_candidates_from_supabase,
    ranked_products,
    read_products_csv,
)
from .config import ROOT_DIR
from .dmm_client import fetch_items
from .sales_importer import import_sales
from .social_mix import build_social_mix


def _default_data_path(name: str) -> Path:
    return ROOT_DIR / "data" / name


def score_products(args: argparse.Namespace) -> None:
    if args.source == "supabase":
        from .supabase_client import fetch_products

        products = fetch_products(
            limit=args.fetch_limit,
            sale_only=not args.include_non_sale,
            min_discount_percent=args.min_discount_percent,
            require_affiliate_url=not args.allow_missing_affiliate_url,
        )
    else:
        products = read_products_csv(args.source)
    rows = []
    for product, detail, bucket in ranked_products(products):
        rows.append(
            {
                "product_code": product.product_code,
                "title": product.title,
                "sale_price": product.sale_price,
                "score": detail["total_score"],
                "bucket": bucket,
                "score_detail": json.dumps(detail, ensure_ascii=False),
            }
        )

    output = sys.stdout if args.output == "-" else open(args.output, "w", newline="", encoding="utf-8")
    writer = csv.DictWriter(
        f=output,
        fieldnames=["product_code", "title", "sale_price", "score", "bucket", "score_detail"],
    )
    writer.writeheader()
    writer.writerows(rows)
    if output is not sys.stdout:
        output.close()


def generate_candidates_command(args: argparse.Namespace) -> None:
    if args.source == "supabase":
        candidates, output_path = generate_candidates_from_supabase(
            limit=args.limit,
            output=args.output,
            fetch_limit=args.fetch_limit,
            sale_only=not args.include_non_sale,
            min_discount_percent=args.min_discount_percent,
            require_affiliate_url=not args.allow_missing_affiliate_url,
        )
    else:
        candidates, output_path = generate_candidates_from_csv(
            source=args.source,
            limit=args.limit,
            output=args.output,
        )
    print(f"generated {len(candidates)} candidates: {output_path}")


def fetch_dmm_command(args: argparse.Namespace) -> None:
    products = fetch_items(
        keyword=args.keyword,
        site=args.site,
        service=args.service,
        floor=args.floor,
        hits=args.hits,
        offset=args.offset,
        sort=args.sort,
    )
    for product in products:
        print(json.dumps(product.__dict__, ensure_ascii=False, default=str))


def import_sales_command(args: argparse.Namespace) -> None:
    output = args.output or _default_data_path("sales.csv")
    rows, path = import_sales(args.source, output)
    print(f"imported {len(rows)} sales rows: {path}")


def generate_social_mix_command(args: argparse.Namespace) -> None:
    if args.refresh_candidates:
        generate_candidates_from_supabase(
            limit=args.limit,
            output=args.candidates,
            fetch_limit=args.fetch_limit,
            sale_only=True,
            min_discount_percent=args.min_discount_percent,
            require_affiliate_url=True,
        )

    posts = build_social_mix(
        candidate_csv=args.candidates,
        normal_count=args.normal_count,
        no_link_count=args.no_link_count,
        affiliate_count=args.affiliate_count,
    )
    for index, post in enumerate(posts, start=1):
        print(f"--- {index}. {post['type']} {post['product_code']}".rstrip())
        print(post["text"])
        print()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="DMM/FANZA affiliate local MVP tools.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    score = subparsers.add_parser("score-products", help="Score products from CSV or Supabase.")
    score.add_argument("--source", default=str(_default_data_path("products.csv")))
    score.add_argument("--fetch-limit", type=int, default=300, help="Maximum products to fetch when source is supabase.")
    score.add_argument("--include-non-sale", action="store_true", help="Include non-sale products when source is supabase.")
    score.add_argument("--min-discount-percent", type=float, default=0.0, help="Minimum discount percent when source is supabase.")
    score.add_argument(
        "--allow-missing-affiliate-url",
        action="store_true",
        help="Include products without affiliate_url when source is supabase.",
    )
    score.add_argument("--output", default="-")
    score.set_defaults(func=score_products)

    generate = subparsers.add_parser("generate-candidates", help="Generate post candidates from CSV or Supabase.")
    generate.add_argument("--source", default=str(_default_data_path("products.csv")))
    generate.add_argument("--limit", type=int, default=5, help="Maximum number of products to turn into candidates.")
    generate.add_argument("--fetch-limit", type=int, default=300, help="Maximum products to fetch when source is supabase.")
    generate.add_argument("--include-non-sale", action="store_true", help="Include non-sale products when source is supabase.")
    generate.add_argument("--min-discount-percent", type=float, default=0.0, help="Minimum discount percent when source is supabase.")
    generate.add_argument(
        "--allow-missing-affiliate-url",
        action="store_true",
        help="Include products without affiliate_url when source is supabase.",
    )
    generate.add_argument("--output", default=str(_default_data_path("post_candidates.csv")))
    generate.set_defaults(func=generate_candidates_command)

    fetch = subparsers.add_parser("fetch-dmm", help="Fetch products from DMM/FANZA API.")
    fetch.add_argument("--keyword", default=None)
    fetch.add_argument("--site", default="FANZA")
    fetch.add_argument("--service", default="digital")
    fetch.add_argument("--floor", default=None)
    fetch.add_argument("--hits", type=int, default=20)
    fetch.add_argument("--offset", type=int, default=1)
    fetch.add_argument("--sort", default="review")
    fetch.set_defaults(func=fetch_dmm_command)

    sales = subparsers.add_parser("import-sales", help="Normalize DMM/FANZA sales CSV.")
    sales.add_argument("--source", required=True)
    sales.add_argument("--output", default=str(_default_data_path("sales.csv")))
    sales.set_defaults(func=import_sales_command)

    social = subparsers.add_parser("generate-social-mix", help="Generate normal posts plus affiliate post drafts.")
    social.add_argument("--candidates", default=str(_default_data_path("post_candidates.csv")))
    social.add_argument("--refresh-candidates", action="store_true")
    social.add_argument("--limit", type=int, default=5)
    social.add_argument("--fetch-limit", type=int, default=300)
    social.add_argument("--min-discount-percent", type=float, default=30.0)
    social.add_argument("--normal-count", type=int, default=2)
    social.add_argument("--no-link-count", type=int, default=1)
    social.add_argument("--affiliate-count", type=int, default=1)
    social.set_defaults(func=generate_social_mix_command)

    return parser


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
