-- Itens de pedido com os dados do cabeçalho e os valores já calculados.
with details as (
    select * from {{ ref('stg_sales__order_details') }}
),

headers as (
    select * from {{ ref('stg_sales__order_headers') }}
),

products as (
    select product_id, standard_cost from {{ ref('stg_production__products') }}
)

select
    d.sales_order_detail_id                                 as sales_order_line_id,
    d.sales_order_id,
    h.sales_order_number,
    h.order_date,
    h.ship_date,
    h.customer_id,
    h.territory_id,
    h.sales_person_id,
    h.is_online_order,
    d.product_id,
    d.special_offer_id,
    d.order_qty,
    d.unit_price,
    d.unit_price_discount,
    d.unit_price * d.order_qty                              as gross_amount,
    d.unit_price * d.order_qty * d.unit_price_discount      as discount_amount,
    d.line_total                                            as net_amount,
    p.standard_cost * d.order_qty                           as cost_amount
from details d
join headers h on h.sales_order_id = d.sales_order_id
left join products p on p.product_id = d.product_id
