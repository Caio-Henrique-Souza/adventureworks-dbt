-- Valores não podem ser negativos e o líquido não pode passar do bruto.
select *
from {{ ref('fct_sales') }}
where order_qty <= 0
   or net_amount < 0
   or net_amount > gross_amount + 0.01
