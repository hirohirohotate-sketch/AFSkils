from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from .config import get_settings
from .models import PostCandidate, Product
from .scoring import bucket_item


def _clean_tag(value: str | None) -> str | None:
    if not value or value == "未設定":
        return None
    primary = re.split(r"[、,，/／・\s]+", value)[0]
    tag = re.sub(r"\s+", "", primary)
    tag = re.sub(r"[#＃]", "", tag)
    return tag or None


def _price(value: int | None) -> str:
    return f"{value:,}円" if value else "価格未設定"


def _price_line(product: Product) -> str:
    if product.normal_price and product.sale_price:
        return f"通常{_price(product.normal_price)} ➔ {_price(product.sale_price)}。"
    if product.sale_price:
        return f"今だけ{_price(product.sale_price)}。"
    return "セール価格はリンク先で確認できます。"


def _actress_label(product: Product) -> str:
    if not product.actress or product.actress == "未設定":
        return "対象作品"
    return f"{product.actress}さん"


def _safe_title(title: str) -> str:
    cleaned = re.sub(r"【[^】]*】", "", title)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = re.split(r"[。！？!?\n]", cleaned)[0].strip()
    direct_terms = (
        "中出し",
        "射精",
        "SEX",
        "セックス",
        "フェラ",
        "精子",
        "乱交",
        "チ○",
        "チン",
        "ハメ",
        "イカせ",
        "抜き",
        "勃起",
        "乳首",
        "媚薬",
        "肉便器",
        "レイプ",
        "孕",
        "ごっくん",
    )
    for term in direct_terms:
        cleaned = cleaned.replace(term, "")
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" 　・、,。")
    if not cleaned:
        return "人気VR作品"
    if len(cleaned) > 28:
        cleaned = cleaned[:28].rstrip(" 　・、,。") + "…"
    return cleaned


def _work_kind(product: Product) -> str:
    title = product.title or ""
    if "準新作" in title:
        return "準新作VR"
    if "初VR" in title or "VR解禁" in title:
        return "初VR"
    if "8K" in title:
        return "8KVR"
    return "人気VR"


def _discount_phrase(product: Product) -> str:
    if product.discount_percent >= 50:
        return "半額以下"
    if product.discount_percent > 0:
        return f"{int(product.discount_percent)}%OFF"
    if product.normal_price and product.sale_price and product.sale_price < product.normal_price:
        return "セール価格"
    return "大特価"


def _appeal_line(product: Product) -> str:
    title = product.title or ""
    actress = product.actress or ""
    if "雨" in title or "豪雨" in title:
        return "雨宿り先で距離が近づくシチュが刺さります…！"
    if "夜行バス" in title or "フェス" in title:
        return "移動中のゼロ距離シチュが近すぎます…！"
    if "キス" in title or "彼女" in title:
        return "近い距離で甘えてくる彼女感が可愛すぎます…！"
    if "学園" in title or "クラス" in title or "放課後" in title:
        return "学園シチュの距離感がVRと相性よすぎます…！"
    if "美少女" in title or "天使" in title:
        return "美少女系VRをまとめて楽しみたい人に刺さります…！"
    if "ハーレム" in title:
        return "複数人シチュの没入感を8Kで楽しめます…！"
    if "初VR" in title or "VR解禁" in title:
        return f"{actress}さんの初VRを安く見られるタイミングです…！" if actress else "初VRを安く見られるタイミングです…！"
    if "ナース" in title or "入院" in title:
        return "包み込んでくれるナース系シチュが相性よさそうです…！"
    if "女上司" in title:
        return "女上司との距離感が近いシチュが刺さります…！"
    if "8K" in title:
        return "8K対応の没入感をセール価格で試せます…！"
    return "シチュエーション重視でVR向きの一本です…！"


def _deadline(product: Product) -> str:
    return product.deadline or "期間限定"


def _deadline_until(deadline: str) -> str:
    if deadline.startswith("残り"):
        return deadline
    if deadline.endswith("まで") or deadline.endswith("中"):
        return deadline
    return f"{deadline}まで"


def _deadline_reason(deadline: str) -> str:
    if deadline.startswith("残り"):
        return f"{deadline}なので"
    if deadline.endswith("まで") or deadline.endswith("中"):
        return f"{deadline}なので"
    return f"{deadline}までなので"


def _deadline_end(deadline: str) -> str:
    if deadline.startswith("残り"):
        return f"{deadline}です"
    if deadline.endswith("まで") or deadline.endswith("中"):
        return f"{deadline}です"
    return f"{deadline}までです"


def _hashtags(product: Product, bucket: str) -> str:
    actress_tag = _clean_tag(product.actress)
    tags: list[str] = []
    if actress_tag:
        tags.append(f"#{actress_tag}")
    if bucket == "cheap_sale_traffic":
        tags.extend(["#FANZA", "#100円セール", "#PR"])
    else:
        tags.extend(["#VR動画", "#FANZA", "#セール"])
    return " ".join(dict.fromkeys(tags))


def _experiment_id(product: Product, variant: str) -> str:
    stamp = datetime.now().strftime("%Y%m%d")
    code = product.product_code or "unknown"
    return f"{stamp}-{code}-{variant}"


def _candidate(
    product: Product,
    score_detail: dict[str, Any],
    bucket: str,
    variant: str,
    template_type: str,
    text: str,
    reward_type: str,
    notes: str = "",
) -> PostCandidate:
    return PostCandidate(
        product_code=product.product_code,
        product_name=product.title,
        actress=product.actress,
        genre=product.genre,
        template_type=template_type,
        variant=variant,
        experiment_id=_experiment_id(product, variant),
        post_text=text,
        normal_price=product.normal_price,
        sale_price=product.sale_price,
        deadline=product.deadline,
        reward_type=reward_type,
        affiliate_url=product.affiliate_url or "",
        score=float(score_detail["total_score"]),
        score_detail=score_detail,
        bucket=bucket,
        notes=notes,
    )


def generate_individual_vr_posts(product: Product, score_detail: dict[str, Any]) -> list[PostCandidate]:
    settings = get_settings()
    bucket = bucket_item(product.sale_price, float(score_detail.get("expected_commission", 0)))
    title = _safe_title(product.title or "対象作品")
    actress = _actress_label(product)
    deadline = _deadline(product)
    price_line = _price_line(product)
    tags = _hashtags(product, bucket)
    url = product.affiliate_url or ""

    if bucket == "cheap_sale_traffic":
        template_type = "100円/大型セール型"
        drafts = [
            (
                "price_first",
                "\n".join(
                    [
                        "【激アツ】",
                        f"FANZA対象作品が今だけ{_price(product.sale_price)}。",
                        f"{_deadline_until(deadline)}のセール対象です。",
                        "",
                        "安く試したい人は一覧から確認できます。",
                        tags,
                        url,
                    ]
                ),
                "100円/低価格セールのクリック回収",
            ),
            (
                "deadline_first",
                "\n".join(
                    [
                        f"【{_deadline_until(deadline)}】",
                        f"FANZAのセール対象が{_price(product.sale_price)}。",
                        "対象作品をまとめて確認できます。",
                        "",
                        tags,
                        url,
                    ]
                ),
                "期限を先頭に出す低価格セール",
            ),
            (
                "actress_first",
                "\n".join(
                    [
                        "【セール情報】",
                        f"{actress}が{_price(product.sale_price)}。",
                        f"{_deadline_reason(deadline)}、価格が戻る前に確認できます。",
                        "",
                        tags,
                        url,
                    ]
                ),
                "女優名から入る低価格セール",
            ),
        ]
    else:
        template_type = "単品VRセール型"
        work_kind = _work_kind(product)
        discount_phrase = _discount_phrase(product)
        appeal = _appeal_line(product)
        chance = f"{_deadline_until(deadline)}なのでこのチャンスをお見逃しなく！"
        drafts = [
            (
                "price_first",
                "\n".join(
                    [
                        "【VRセール情報】",
                        f"{actress}の{work_kind}『{title}』",
                        f"今なら{discount_phrase}の大特価！",
                        price_line,
                        "",
                        appeal,
                        chance,
                        "",
                        tags,
                        url,
                    ]
                ),
                "価格差から始める",
            ),
            (
                "deadline_first",
                "\n".join(
                    [
                        "【VRセール情報】",
                        f"{actress}の{work_kind}『{title}』",
                        f"{_deadline_until(deadline)}のセール対象！",
                        price_line,
                        "",
                        appeal,
                        "価格が戻る前にこのチャンスをお見逃しなく！",
                        "",
                        tags,
                        url,
                    ]
                ),
                "期限から始める",
            ),
            (
                "actress_first",
                "\n".join(
                    [
                        "【VRセール情報】",
                        f"{actress}の{work_kind}『{title}』",
                        f"今なら{discount_phrase}の大特価！",
                        price_line,
                        "",
                        appeal,
                        chance,
                        "",
                        tags,
                        url,
                    ]
                ),
                "女優名から始める",
            ),
        ]

    return [
        _candidate(
            product=product,
            score_detail=score_detail,
            bucket=bucket,
            variant=variant,
            template_type=template_type,
            text=text,
            reward_type=settings.default_reward_type,
            notes=notes,
        )
        for variant, text, notes in drafts
    ]
