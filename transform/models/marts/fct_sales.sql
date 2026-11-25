-- Fato de vendas. Grão: um item de pedido.
select
    sales_order_line_id,
    sales_order_id,
    sales_order_number,
    order_date,
    ship_date,
    customer_id,
    product_id,
    territory_id,
    sales_person_id,
    is_online_order,
    case when is_online_order then 'Online' else 'Revenda' end  as sales_channel,
    order_qty,
    unit_price,
    unit_price_discount,
    gross_amount,
    discount_amount,
    net_amount,
    cost_amount,
    net_amount - cost_amount                                    as margin_amount
from {{ ref('int_sales__order_lines') }}
