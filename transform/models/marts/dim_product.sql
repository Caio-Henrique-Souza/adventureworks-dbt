with products as (
    select * from {{ ref('stg_production__products') }}
),

subcategories as (
    select * from {{ ref('stg_production__product_subcategories') }}
),

categories as (
    select * from {{ ref('stg_production__product_categories') }}
),

models as (
    select * from {{ ref('stg_production__product_models') }}
)

select
    p.product_id,
    p.product_number,
    p.product_name,
    coalesce(c.product_category_name, 'Sem categoria')       as product_category,
    coalesce(s.product_subcategory_name, 'Sem subcategoria') as product_subcategory,
    m.product_model_name                                     as product_model,
    p.product_line,
    p.color,
    p.size,
    p.is_finished_good,
    p.standard_cost,
    p.list_price,
    p.sell_start_date,
    p.sell_end_date,
    p.discontinued_date
from products p
left join subcategories s on s.product_subcategory_id = p.product_subcategory_id
left join categories c on c.product_category_id = s.product_category_id
left join models m on m.product_model_id = p.product_model_id
