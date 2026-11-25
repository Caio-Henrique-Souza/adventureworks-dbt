-- Todo território que vendeu num mês precisa ter meta na planilha do comercial.
select month_start, territory_name, actual_amount
from {{ ref('fct_sales_vs_target_monthly') }}
where target_amount is null and actual_amount > 0
