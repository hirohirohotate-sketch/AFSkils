from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from .models import PostCandidate


POST_CANDIDATE_FIELDS = [
    "created_at",
    "account_id",
    "product_code",
    "product_name",
    "actress",
    "genre",
    "template_type",
    "variant",
    "experiment_id",
    "post_text",
    "normal_price",
    "sale_price",
    "deadline",
    "reward_type",
    "affiliate_url",
    "score",
    "bucket",
    "score_detail",
    "notes",
]


def write_post_candidates(
    candidates: Iterable[PostCandidate],
    output_path: str | Path,
    account_id: str,
    created_at: str,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=POST_CANDIDATE_FIELDS)
        writer.writeheader()
        for candidate in candidates:
            row = asdict(candidate)
            row["created_at"] = created_at
            row["account_id"] = account_id
            row["score_detail"] = json.dumps(candidate.score_detail, ensure_ascii=False)
            writer.writerow({field: row.get(field, "") for field in POST_CANDIDATE_FIELDS})

    return path
