-- A soma dos itens precisa bater com o subtotal do cabeçalho de cada pedido (tolerância de 1 centavo).
select
    h.sales_order_id,
    h.subtotal,
    sum(f.net_amount) as soma_itens
from {{ ref('stg_sales__order_headers') }} h
join {{ ref('fct_sales') }} f on f.sales_order_id = h.sales_order_id
group by h.sales_order_id, h.subtotal
having abs(h.subtotal - sum(f.net_amount)) > 0.01
