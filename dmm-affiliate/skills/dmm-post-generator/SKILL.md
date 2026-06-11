---
name: dmm-post-generator
description: Generate Japanese X post drafts, blog intro copy, hashtag candidates, and CSV tracking rows for DMM affiliate sale/product promotion. Use when the user provides product information, sale information, a DMM affiliate URL, or asks to create local draft posts from templates such as VR sale, 100 yen sale, ranking, comparison, deadline urgency, or blog referral. Do not use for automatic posting.
---

# DMM Post Generator

## Purpose

Create draft posts for manual X posting from product and sale inputs. Optimize for learning which message type gets clicks and conversions, not for automation.

## Required Inputs

Ask for missing fields only if the post cannot be drafted without them. Otherwise, use `未設定` and keep moving.

```text
商品名:
女優名:
ジャンル:
通常価格:
セール価格:
期限:
報酬タイプ: direct / category
URL:
一言メモ:
使う型: VRセール / 100円セール / 冒険
```

## Output Format

Return exactly these sections:

1. `売れた型ベース投稿`
   - 7 drafts by default.
   - Use `単品VRセール型` and `100円/大型セール型` unless the input clearly says otherwise.
2. `冒険投稿`
   - 3 drafts by default.
   - Use ranking, comparison, deadline urgency, and blog referral patterns.
3. `ブログ用紹介文`
   - 1 short paragraph, 120-180 Japanese characters.
4. `ハッシュタグ候補`
   - 5-8 tags.
5. `CSV記録用の行`
   - Use the `data/posts.csv` column order.

## Writing Rules

- Keep each X draft around 70-120 Japanese characters before the URL.
- Include one clear reason to click: price gap, deadline, genre fit, ranking angle, or comparison angle.
- Do not claim sales rank, discount rate, stock, deadline, or performance if the input does not provide it.
- Avoid explicit sexual wording. Keep copy focused on sale value, title/actor, genre, and browsing intent.
- Avoid vague hype such as `神`, `最高`, `絶対`, `爆売れ` unless the user provides evidence.
- Do not auto-post, schedule posts, or call external APIs. Output drafts only.
- If the product is adult-oriented, keep the language platform-safe and do not intensify explicit details.

## Template Selection

Use `templates.md` for reusable post patterns. Use `examples.md` only when the user asks for examples or the draft feels too abstract.

Default 10-post mix:

| Type | Count |
|---|---:|
| 単品VRセール型 | 4 |
| 100円/大型セール型 | 3 |
| 冒険型 | 3 |

If the user asks for one day of 8 posts, use:

| Type | Count |
|---|---:|
| 単品VRセール型 | 3 |
| 100円/大型セール型 | 3 |
| 冒険型 | 2 |

## CSV Row Rules

Create one row per generated draft. Leave metrics blank until after posting.

Required column order:

```csv
date,post_url,product_name,actress,genre,template_type,variant,normal_price,sale_price,deadline,reward_type,affiliate_url,impressions,clicks,conversions,revenue_yen,ctr_percent,cvr_percent,notes
```

Use `variant` values like `A1`, `A2`, `B1`, `ADV1`. Put the draft text or hypothesis in `notes` if useful.
