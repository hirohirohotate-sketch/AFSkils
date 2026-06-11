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
   - Also include 2-4 default hashtags at the end of every X draft, after the URL.
5. `CSV記録用の行`
   - Use the `data/posts.csv` column order.

## Writing Rules

実績のある2つの投稿フォーマットを起点にする。

**単品VRセール型（direct報酬）の基本ルール：**
- `【VRセール情報】` で始める（固定）
- 女優名は `さん` 付き、商品名は `『』` で括る
- 8KVR版と通常版の2つの価格を `➔` で並べる（片方しかなければ1つでよい）
- 一言メモは内容の具体的な特徴を感情込みで1文。「〜すぎます…！」のトーンでよい
- 締めは「このチャンスをお見逃しなく！」で統一
- ハッシュタグに女優名を必ず含める
- ハッシュタグはURLの**前**に置く

**100円/大型セール型（カテゴリ報酬）の基本ルール：**
- `【激アツ】` で始める（固定）
- 「神セール」「全品〇〇円」で規模感を出す。`神` は使ってよい
- 対象本数と期限を必ず入れる
- `#PR` を含める
- `#エロ動画` など直接的なジャンルタグを入れる
- ハッシュタグはURLの**前**に置く

**共通ルール：**
- Do not auto-post, schedule posts, or call external APIs. Output drafts only.
- 性的な表現は直接的に書かない。内容の雰囲気や状況描写にとどめる。
- 入力にない情報（ランキング、在庫数、実績）を捏造しない。
- バリエーションは書き出しや価格の見せ方で変化をつける。同じ文体を繰り返さない。

## 禁止パターン（以下の言い回しは使わない）

- 「あとで見ようとして忘れるやつ」
- 「先に貼る」
- 「今日中に見とくとよさそう」
- 「期限かなり近い」
- 「失敗コスト低め」
- 「〜で探している人向け」
- 「確認候補」「投稿枠」「訴求」「比較用に置いておく」
- バリアントラベル `[A1 / 単品VRセール型]` などを投稿本文に含める

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
