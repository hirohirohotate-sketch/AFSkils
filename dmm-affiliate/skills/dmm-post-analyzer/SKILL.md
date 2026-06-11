---
name: dmm-post-analyzer
description: Analyze local DMM affiliate post performance CSVs and produce weekly Japanese reports that decide which post templates to keep, pause, or change. Use when the user provides data/posts.csv, weekly post metrics, impressions, clicks, conversions, affiliate revenue, or asks for a weekly report, template judgment, CTR/CVR analysis, or next-week posting allocation.
---

# DMM Post Analyzer

## Purpose

Read post performance data and decide the next action by template. Prioritize clicks and conversions over impressions.

## Input

Use `data/posts.csv` by default. Expected columns:

```csv
date,post_url,product_name,actress,genre,template_type,variant,normal_price,sale_price,deadline,reward_type,affiliate_url,impressions,clicks,conversions,revenue_yen,ctr_percent,cvr_percent,notes
```

Use `metrics.md` when column definitions, threshold details, or allocation rules need to be checked.

If `ctr_percent` or `cvr_percent` is blank, calculate:

- `ctr_percent = clicks / impressions * 100`
- `cvr_percent = conversions / clicks * 100`

Do not calculate CVR when clicks are zero.

## Weekly Report Format

Return exactly these sections:

1. `結論`
   - One line. Say which template mix to use next week.
2. `数字`
   - Table by `template_type`: posts, impressions, clicks, CTR, conversions, revenue.
3. `残す型`
   - Templates meeting the keep criteria.
4. `捨てる/止める型`
   - Templates below threshold or with no useful learning.
5. `修正する型`
   - Templates with impressions but weak clicks, or clicks but weak conversions.
6. `来週の投稿配分`
   - Convert the decision into daily counts for 8 posts/day.
7. `今週やること`
   - Maximum 3 concrete actions.

## Decision Rules

Use these thresholds unless the user gives stronger business constraints:

| Metric | Judgment |
|---|---|
| 100 impressions per 2+ clicks | Keep |
| 100 impressions per fewer than 1 click | Weak |
| Any conversion | Prioritize and templatize |
| High impressions with low clicks | Hook/value mismatch |
| Clicks with no conversion | Landing/product/price mismatch |

Minimum sample rule:

- Do not kill a template from fewer than 10 posts unless CTR is clearly zero.
- Promote a template immediately if it gets a conversion.
- If total clicks are fewer than 20, treat conclusions as provisional.

## Business Framing

Tie recommendations back to the current target:

| Item | Value |
|---|---:|
| Monthly revenue target | 20,000 yen |
| Daily work time | 2 hours |
| Daily post target | 8 posts |
| Two-week validation target | about 100 posts |

Avoid generic advice such as SEO or social growth. Recommend only actions that fit local manual posting and CSV tracking.
