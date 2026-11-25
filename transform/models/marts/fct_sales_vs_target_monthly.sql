-- Realizado x meta por território e mês. A meta vem da planilha Excel do comercial.
with realizado as (
    select
        date_trunc('month', f.order_date)::date as month_start,
        t.territory_name,
        sum(f.net_amount)                       as actual_amount,
        count(distinct f.sales_order_id)        as orders
    from {{ ref('fct_sales') }} f
    join {{ ref('dim_territory') }} t on t.territory_id = f.territory_id
    group by all
),

metas as (
    select target_month as month_start, territory_name, target_amount, owner_name
    from {{ ref('stg_excel__sales_targets') }}
)

select
    coalesce(r.month_start, m.month_start)          as month_start,
    coalesce(r.territory_name, m.territory_name)    as territory_name,
    m.owner_name,
    coalesce(r.actual_amount, 0)                    as actual_amount,
    m.target_amount,
    coalesce(r.orders, 0)                           as orders,
    case when m.target_amount > 0
         then coalesce(r.actual_amount, 0) / m.target_amount end as target_attainment
from realizado r
full outer join metas m
    on m.month_start = r.month_start
   and m.territory_name = r.territory_name
