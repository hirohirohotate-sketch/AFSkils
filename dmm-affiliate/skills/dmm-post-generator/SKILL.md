---
name: dmm-post-generator
description: Generate Japanese X post drafts, blog intro copy, hashtag candidates, and CSV tracking rows for DMM affiliate sale/product promotion. Use when the user provides product information, sale information, a DMM affiliate URL, or asks to create local draft posts from templates such as VR sale, 100 yen sale, ranking, comparison, deadline urgency, or blog referral. Do not use for automatic posting.
---

# DMM Post Generator

## Purpose

Create draft posts for manual X posting from product and sale inputs. Optimize for learning which message type gets clicks and conversions, not for automation.

## Automatic Flow Trigger

When the user says `投稿文作って`, `投稿文を作って`, or asks for the next post draft, do not stop at analysis. Use the current repository CLI to fetch candidates and produce drafts:

```bash
poetry run dmm-affiliate generate-candidates --source supabase --limit 5 --min-discount-percent 30
```

Then read `data/post_candidates.csv` and output selected post drafts. For a new account, include normal non-link posts as well as affiliate posts. Do not ask which product to use unless Supabase access fails or no candidates are available. Do not auto-post.

Default mix for a new account:

| Type | Count |
|---|---:|
| 普通のVR雑談・選び方メモ | 2 |
| URLなしセールメモ | 1 |
| アフィリURLあり投稿 | 1 |

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
   - Use `単品VRセール型`, `期限型`, and `価格差型` for normal daily generation.
   - Use `100円/大型セール型` only when the input explicitly says `100円セール`, `大型セール`, `カテゴリ報酬`, target count, or an event sale URL.
2. `冒険投稿`
   - 3 drafts by default.
   - Use ranking, comparison, deadline urgency, and blog referral patterns.
3. `ブログ用紹介文`
   - 1 short paragraph, 120-180 Japanese characters.
4. `ハッシュタグ候補`
   - 5-8 tags.
   - Also include 2-4 default hashtags in every X draft, before the URL.
5. `CSV記録用の行`
   - Use the `data/posts.csv` column order.

## Writing Rules

実績のある2つの投稿フォーマットを起点にする。

**単品VRセール型（direct報酬）の基本ルール：**
- `【VRセール情報】` で始める（固定）
- 女優名は `さん` 付き、商品名は `『』` で括る
- 8KVR版と通常版の2つの価格を `➔` で並べる（片方しかなければ1つでよい）
- 一言メモは内容の具体的な特徴を感情込みで1文。「〜すぎます…！」のトーンでよい
- 締めは「このチャンスをお見逃しなく！」を基本にする。期限がある場合は直前に入れる。
- ハッシュタグに女優名を必ず含める
- ハッシュタグはURLの**前**に置く

**100円/大型セール型（カテゴリ報酬）の基本ルール：**
- これは常設テンプレではなくイベント枠。通常の個別商品生成では使わない。
- 入力に `100円セール`、`大型セール`、`カテゴリ報酬`、対象本数、イベントURLのいずれかがある場合だけ使う。
- `【激アツ】` で始める（固定）
- 「神セール」「全品〇〇円」で規模感を出す。`神` は使ってよい
- 対象本数と期限を必ず入れる
- `#PR` を含める
- 直接的すぎるジャンルタグは避け、商品種別・セール情報・ブランド名を中心にする
- ハッシュタグはURLの**前**に置く

**共通ルール：**
- Do not auto-post, schedule posts, or call external APIs. Output drafts only.
- 性的な表現は直接的に書かない。内容の雰囲気や状況描写にとどめる。
- 入力にない情報（ランキング、在庫数、実績）を捏造しない。
- バリエーションは書き出しや価格の見せ方で変化をつける。同じ文体を繰り返さない。
- ハッシュタグはURLの前に置く。投稿本文 → ハッシュタグ → URL の順番にする。
- 新規アカウントではアフィリURLあり投稿だけを連投しない。普通投稿とURLなし投稿を混ぜる。

## Normal Non-Link Post Rules

普通投稿は売り込まない。URL、価格、特定作品名、`#FANZA`、`#セール` を入れない。

使うテーマ:

- VR作品の選び方
- 価格帯の考え方
- 距離感、目線、没入感
- 8KVRと通常版の違い
- セールで外しにくい見方

例:

```text
VR作品って、価格よりも「距離感」が合うかどうかで満足度かなり変わる気がする。
```

```text
セールで見るなら、まず500〜900円台から試すのが一番外しにくい。
```

```text
女優名で選ぶより、シチュエーションで選んだ方が当たり引きやすい時ある。
```

## No-Link Sale Memo Rules

URLなしセールメモは、セール傾向だけを書く。特定URLに誘導しない。

```text
今日見た感じ、500〜900円台のVRセールが多め。
いきなり高いのを買うより、この価格帯で相性を見る方がよさそう。
```

## Link Click Optimization Rules

- 投稿の最初の2行で「誰の何が、いくらで、いつまで」を必ず伝える。
- URL前の本文は120文字前後を目安にする。
- 1投稿につき紹介する商品またはセールは1つだけにする。
- クリック理由は「価格差」「期限」「対象本数」「セール対象」のいずれかにする。
- レビュー件数や評価は商品選定に使う。投稿本文では基本的に出さない。
- 価格差の後に、商品タイトルを短く言い換えたシチュエーションの一言を入れる。
- 「このチャンスをお見逃しなく！」で締め、直前に期限があれば入れる。
- バリエーションは以下の3種類を基本にする。
  - price_first: 価格差から始める
  - deadline_first: 期限から始める
  - actress_first: 女優名から始める
- 運用者目線の言い回しは避ける。
  - NG: 確認候補、投稿枠、訴求、検証用、拾っておきたい
- 投稿文はプラットフォームで止まりにくい表現に寄せる。
- 直接的な性的表現は避け、商品種別・価格・期限・女優名・セール情報を中心にする。

## 禁止パターン（以下の言い回しは使わない）

- 「あとで見ようとして忘れるやつ」
- 「先に貼る」
- 「今日中に見とくとよさそう」
- 「期限かなり近い」
- 「失敗コスト低め」
- 「〜で探している人向け」
- 「確認候補」「投稿枠」「訴求」「比較用に置いておく」
- 「検証用」「拾っておきたい」
- バリアントラベル `[A1 / 単品VRセール型]` などを投稿本文に含める

## Template Selection

Use `templates.md` for reusable post patterns. Use `examples.md` only when the user asks for examples or the draft feels too abstract.

通常日は個別VR/direct型を優先する。100円/大型セール型は常時使える商品ではないため、入力にセールイベント情報がある場合だけ差し替える。

Default 10-post mix:

| Type | Count |
|---|---:|
| 単品VRセール型 | 5 |
| 期限型 | 2 |
| 価格差型/冒険型 | 3 |

If the user asks for one day of 8 posts, use:

| Type | Count |
|---|---:|
| 単品VRセール型 | 4 |
| 期限型 | 2 |
| 価格差型 | 1 |
| 冒険型 | 1 |

For a new or warmed-up account, prefer this daily mix:

| Type | Count |
|---|---:|
| 普通のVR雑談・選び方メモ | 2 |
| URLなしセールメモ | 1 |
| アフィリURLあり投稿 | 1 |

If an active 100 yen or large category sale is explicitly provided, replace part of the daily mix:

| Type | Count |
|---|---:|
| 単品VRセール型 | 3 |
| 期限型 | 2 |
| 100円/大型セール型 | 2 |
| 冒険型 | 1 |

## CSV Row Rules

Create one row per generated draft. Leave metrics blank until after posting.

Required column order:

```csv
date,post_url,product_name,actress,genre,template_type,variant,normal_price,sale_price,deadline,reward_type,affiliate_url,impressions,clicks,conversions,revenue_yen,ctr_percent,cvr_percent,notes
```

Use `variant` values like `A1`, `A2`, `B1`, `ADV1`. Put the draft text or hypothesis in `notes` if useful.
