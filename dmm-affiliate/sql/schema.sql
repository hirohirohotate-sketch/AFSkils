create table if not exists products (
  id bigserial primary key,
  product_code text unique,
  title text not null,
  actress text,
  genre text,
  maker text,
  normal_price integer,
  sale_price integer,
  review_count integer default 0,
  review_average numeric,
  discount_percent numeric default 0,
  deadline text,
  affiliate_url text,
  content_url text,
  image_url text,
  raw_json jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create index if not exists idx_products_sale_price
  on products (sale_price);

create index if not exists idx_products_discount_percent
  on products (discount_percent);

create index if not exists idx_products_created_at
  on products (created_at desc);

create table if not exists post_candidates (
  id bigserial primary key,
  product_code text,
  account_id text,
  template_type text,
  variant text,
  experiment_id text,
  post_text text not null,
  affiliate_url text,
  score numeric,
  bucket text,
  score_detail jsonb,
  status text default 'draft',
  created_at timestamptz default now()
);

create table if not exists posted_posts (
  id bigserial primary key,
  candidate_id bigint,
  x_post_url text,
  account_id text,
  product_code text,
  template_type text,
  variant text,
  experiment_id text,
  post_text text,
  posted_at timestamptz,
  created_at timestamptz default now()
);

create table if not exists post_metrics (
  id bigserial primary key,
  posted_post_id bigint,
  impressions integer,
  engagements integer,
  detail_expands integer,
  profile_visits integer,
  link_clicks integer,
  likes integer,
  reposts integer,
  replies integer,
  measured_at timestamptz default now()
);

create table if not exists sales_reports (
  id bigserial primary key,
  sold_at date,
  product_code text,
  product_title text,
  sale_price integer,
  commission_type text,
  commission_count integer,
  commission_yen integer,
  raw_json jsonb,
  created_at timestamptz default now()
);
