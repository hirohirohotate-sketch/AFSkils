# Metrics Reference

## CSV Columns

| Column | Meaning |
|---|---|
| date | Posted date |
| post_url | X post URL |
| product_name | Product title |
| actress | Actress or creator name |
| genre | Product genre |
| template_type | Template category |
| variant | Variant id such as A1 or ADV1 |
| normal_price | Normal price in yen |
| sale_price | Sale price in yen |
| deadline | Sale deadline |
| reward_type | direct or category |
| affiliate_url | Affiliate URL used |
| impressions | X impressions |
| clicks | Affiliate or link clicks |
| conversions | Purchases/conversions |
| revenue_yen | Affiliate reward |
| ctr_percent | clicks / impressions * 100 |
| cvr_percent | conversions / clicks * 100 |
| notes | Hypothesis, post text summary, or manual observation |

## Keep/Pause Thresholds

| Result | Action |
|---|---|
| CTR >= 2.0% | Keep |
| CTR < 1.0% | Pause or rewrite |
| conversions >= 1 | Prioritize |
| impressions high, clicks low | Rewrite hook |
| clicks high, conversions zero | Change product or landing angle |

## Weekly Allocation Rule

For 8 posts/day:

| Template Status | Allocation |
|---|---:|
| Conversion winner | 3-4/day |
| CTR winner without conversion | 2-3/day |
| Learning slot | 1-2/day |
| Weak template | 0/day |

Keep 70% of posts in proven templates and 30% in experiments until there are at least 3 conversion-backed templates.
