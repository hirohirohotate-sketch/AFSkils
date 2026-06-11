# DMM Post Templates

Use placeholders exactly as labels when source data is missing.

## 売れた型

### 単品VRセール型

Intent: Push one concrete product where title, actress, genre, and sale price are enough to create a click reason.

Pattern:

```text
【{女優名} / {ジャンル}】
{商品名} が {通常価格} -> {セール価格}。
VR系を探している人は、期限前に確認しておく枠。
{URL}
```

Variants:

- Price gap first: `通常{通常価格}が{セール価格}`
- Actress first: `{女優名}で探している人向け`
- Deadline first: `{期限}までなので後回しにしない`

### 100円/大型セール型

Intent: Sell the sale event, not one product. Use when the sale price is very low or the campaign has many eligible items.

Pattern:

```text
【{セール価格}セール】
{ジャンル}を安く拾うならこの枠。
まずは{女優名} / {商品名}から確認。
期限: {期限}
{URL}
```

Variants:

- `100円なら失敗コストが低い`
- `まとめ買い候補`
- `カテゴリ報酬向けの入口`

## 冒険型

### ランキング型

Use only if ranking data exists. If no ranking exists, write as `候補`.

```text
【今日の候補】
{ジャンル}で見るなら、まず{商品名}。
価格は{セール価格}、期限は{期限}。
比較用に置いておく。
{URL}
```

### 比較型

```text
同じ{ジャンル}でも、今日は価格差で見る。
{商品名}: {通常価格} -> {セール価格}
{一言メモ}
{URL}
```

### 期限煽り型

```text
期限が{期限}のセール枠。
{商品名}を後で見ようとして忘れる人向けにメモ。
{セール価格}なら先に確認でいい。
{URL}
```

### ブログ誘導型

```text
{ジャンル}のセール候補を整理中。
単品で見るなら{商品名}、比較して選ぶならブログ側にまとめる。
{URL}
```

## Hashtag Rules

- Use 2-4 hashtags per post.
- Prefer broad discovery tags plus sale intent.
- Do not overstuff actress names as hashtags.

Candidates:

```text
#DMM
#FANZA
#セール
#VR
#期間限定
#動画セール
#アフィリエイト検証
```
