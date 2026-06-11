# DMM Post Generator Examples

## Input Example

```text
商品名: サンプルVRタイトル
女優名: サンプル女優
ジャンル: VR
通常価格: 1,980円
セール価格: 550円
期限: 2026-06-20
報酬タイプ: direct
URL: https://example.com/affiliate
一言メモ: 初回検証用。価格差を前に出す。
使う型: VRセール
```

## Output Example

### 売れた型ベース投稿

1. `[A1 / 単品VRセール型] 【サンプル女優 / VR】サンプルVRタイトルが1,980円 -> 550円。VR系を安く確認したい人向け。期限は2026-06-20。 https://example.com/affiliate`
2. `[A2 / 単品VRセール型] サンプル女優でVRを探している人向け。サンプルVRタイトルが550円まで下がっているので、期限前の確認枠。 https://example.com/affiliate`

### 冒険投稿

1. `[ADV1 / 比較型] 同じVRでも今日は価格差で見る。サンプルVRタイトル: 1,980円 -> 550円。初回検証用に価格訴求で出す。 https://example.com/affiliate`

### ブログ用紹介文

サンプルVRタイトルは、通常1,980円から550円に下がっているVRセール候補です。サンプル女優で探している人や、まず価格差の大きい作品から確認したい人向けに記録します。

### ハッシュタグ候補

`#DMM` `#FANZA` `#VR` `#セール` `#期間限定`

### CSV記録用の行

```csv
date,post_url,product_name,actress,genre,template_type,variant,normal_price,sale_price,deadline,reward_type,affiliate_url,impressions,clicks,conversions,revenue_yen,ctr_percent,cvr_percent,notes
2026-06-11,,サンプルVRタイトル,サンプル女優,VR,単品VRセール型,A1,1980,550,2026-06-20,direct,https://example.com/affiliate,,,,,,価格差訴求
```
