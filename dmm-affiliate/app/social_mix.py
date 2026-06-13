from __future__ import annotations

import csv
from pathlib import Path


NORMAL_POSTS = [
    "VR作品って、価格よりも「距離感」が合うかどうかで満足度かなり変わる気がする。",
    "8KVRはハマる作品だと没入感が一気に上がるけど、作品選びを外すと通常版でよかったってなる。",
    "女優名で選ぶより、シチュエーションで選んだ方が当たり引きやすい時ある。",
    "セールで見るなら、まず500〜900円台から試すのが一番外しにくい。",
    "VRは「近い」「目線が合う」「距離が詰まる」系の作品がやっぱり強い。",
]

NO_LINK_SALE_MEMOS = [
    "今日見た感じ、500〜900円台のVRセールが多め。\nいきなり高いのを買うより、この価格帯で相性を見る方がよさそう。",
    "30%OFFでも、元値が高い作品は結局1,000円超えることがある。\n最初は価格帯を見て選ぶ方が外しにくい。",
    "セール作品を見るときは、価格だけじゃなくてシチュエーションが合うかも見た方がいい。",
]


def build_social_mix(candidate_csv: str | Path, normal_count: int = 2, no_link_count: int = 1, affiliate_count: int = 1) -> list[dict[str, str]]:
    posts: list[dict[str, str]] = []

    for text in NORMAL_POSTS[:normal_count]:
        posts.append({"type": "normal", "product_code": "", "text": text})

    for text in NO_LINK_SALE_MEMOS[:no_link_count]:
        posts.append({"type": "no_link_sale_memo", "product_code": "", "text": text})

    with Path(candidate_csv).open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    seen: set[str] = set()
    for row in rows:
        code = row.get("product_code", "")
        if not code or code in seen:
            continue
        if row.get("variant") not in {"price_first", "sold_shape_manual"}:
            continue
        posts.append({"type": "affiliate", "product_code": code, "text": row.get("post_text", "")})
        seen.add(code)
        if len([post for post in posts if post["type"] == "affiliate"]) >= affiliate_count:
            break

    return posts
