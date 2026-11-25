-- Calendário cobrindo do primeiro ao último ano com pedidos.
with limites as (
    select
        make_date(year(min(order_date)), 1, 1)   as data_inicio,
        make_date(year(max(order_date)), 12, 31) as data_fim
    from {{ ref('stg_sales__order_headers') }}
),

dias as (
    select cast(d.range as date) as date_day
    from limites, range(limites.data_inicio, limites.data_fim + interval 1 day, interval 1 day) d
)

select
    date_day,
    year(date_day)                                  as year,
    quarter(date_day)                               as quarter,
    month(date_day)                                 as month,
    strftime(date_day, '%Y-%m')                     as year_month,
    make_date(year(date_day), month(date_day), 1)   as month_start,
    isodow(date_day)                                as day_of_week,
    isodow(date_day) in (6, 7)                      as is_weekend
from dias
