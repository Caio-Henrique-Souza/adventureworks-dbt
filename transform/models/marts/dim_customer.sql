with customers as (
    select * from {{ ref('int_customers__enriched') }}
),

primeira_compra as (
    select customer_id, min(order_date) as first_order_date, max(order_date) as last_order_date
    from {{ ref('stg_sales__order_headers') }}
    group by customer_id
)

select
    c.customer_id,
    c.account_number,
    c.customer_name,
    c.customer_type,
    c.contact_name,
    c.territory_id,
    f.first_order_date,
    f.last_order_date
from customers c
left join primeira_compra f on f.customer_id = c.customer_id
