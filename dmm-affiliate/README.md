# dmm-affiliate

DMM/FANZAアフィリエイト投稿の手動運用を支援するローカルMVPです。目的は自動投稿ではなく、商品候補をスコアリングし、クリックと成約に近い投稿候補を作って人間が手動投稿することです。

## できること

- `data/products.csv` から商品を読み込む
- レビュー数、レビュー平均、価格、報酬見込み、割引率、期限でスコアリングする
- 投稿候補を `data/post_candidates.csv` に出力する
- DMM/FANZA売上CSVを `data/sales.csv` に正規化する
- DMM APIとSupabaseは環境変数がある場合だけ使う

## やらないこと

- X自動投稿
- Xログインやブラウザ操作
- 自動下書き投入
- ダッシュボード
- 自前リダイレクト計測

## セットアップ

```bash
cp .env.example .env
poetry install
```

APIやSupabaseを使わない場合、`.env` のキーは空で構いません。

## 商品データ運用

初期状態では商品候補を `data/products.csv` に入れます。

```csv
product_code,title,actress,genre,maker,normal_price,sale_price,review_count,review_average,discount_percent,deadline,affiliate_url,content_url,image_url
```

Supabaseを使う場合は、同じ内容を `products` テーブルに置きます。既存DBに `works` テーブルがある場合は、`products` が無くても `works` から読みます。

投稿実績は既存の `data/posts.csv` を残し、拡張列が必要な場合は `data/posts_v2.csv` に記録します。

## 候補生成

```bash
poetry run dmm-affiliate generate-candidates --source data/products.csv --limit 5
```

Supabaseの `products` から読む場合:

```bash
poetry run dmm-affiliate generate-candidates --source supabase --limit 5
```

Supabase読み込みでは、デフォルトでセール作品を主体にします。

- `sale_price` がある
- `normal_price` がある場合は `sale_price < normal_price`
- `affiliate_url` がある
- 取得後にレビュー、価格、割引率、期限でスコア順に並べる

割引率を絞る場合:

```bash
poetry run dmm-affiliate generate-candidates --source supabase --limit 5 --min-discount-percent 30
```

セール外も含めたい場合:

```bash
poetry run dmm-affiliate generate-candidates --source supabase --include-non-sale
```

出力:

```text
data/post_candidates.csv
```

候補には `post_text`、`score`、`bucket`、`score_detail`、`affiliate_url` が入ります。
`--limit` は商品数の上限です。各商品から `price_first`、`deadline_first`、`actress_first` の3候補を作ります。

## 投稿文作成の固定フロー

「投稿文作って」と依頼されたら、以下を実行して `data/post_candidates.csv` から投稿文を提示します。

```bash
poetry run dmm-affiliate generate-candidates --source supabase --limit 5 --min-discount-percent 30
```

新規アカウントではアフィリURLあり投稿だけを出さず、普通投稿も混ぜます。

| 種別 | 目安 |
|---|---:|
| 普通のVR雑談・選び方メモ | 2本 |
| URLなしセールメモ | 1本 |
| アフィリURLあり投稿 | 1本 |

1週間検証中はURLあり投稿テンプレを変えず、商品だけ変えます。自動投稿はしません。

普通投稿も混ぜて出す場合:

```bash
poetry run dmm-affiliate generate-social-mix --refresh-candidates
```

## スコア確認

```bash
poetry run dmm-affiliate score-products --source data/products.csv
```

Supabaseの `products` をスコア確認する場合:

```bash
poetry run dmm-affiliate score-products --source supabase
```

## 売上CSV取り込み

```bash
poetry run dmm-affiliate import-sales --source data/sales_report.csv
```

DMM/FANZAのCSV列名が多少変わっても、最低限以下に正規化します。

```text
sold_at, product_code, product_title, sale_price, commission_type, commission_count, commission_yen
```

## DMM API

`.env` に以下を設定した場合だけ使います。

```env
DMM_API_ID=
DMM_AFFILIATE_ID=
```

```bash
poetry run dmm-affiliate fetch-dmm --keyword VR --hits 20
```

APIが使えない場合でも、`products.csv` から候補生成できます。

## Supabase

`.env` に以下がある場合、`products` テーブルから商品候補を読み込めます。

```env
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
```

テーブル定義は `sql/schema.sql` にあります。
新規DBなら、先にSupabaseのSQL Editorで `sql/schema.sql` を実行して、`products` テーブルを作ってください。既存DBに `works` テーブルがある場合は、その構成を優先して読み込みます。

## Docker

```bash
docker compose build
docker compose run --rm affiliate-worker
```

Dockerでも `data/products.csv` から `data/post_candidates.csv` を生成します。

## 次にやること

- 投稿ごとにURLまたは識別子を分ける
- `posts_v2.csv` に投稿文と実績を記録する
- 売上CSVと投稿候補の紐付けルールを追加する
- 2週間分の投稿実績でテンプレ別のCTR/CVRを比較する
