-- Clientes com nome, tipo e território resolvidos.
with customers as (
    select * from {{ ref('stg_sales__customers') }}
),

persons as (
    select person_id, full_name from {{ ref('stg_person__persons') }}
),

stores as (
    select store_id, store_name from {{ ref('stg_sales__stores') }}
)

select
    c.customer_id,
    c.account_number,
    coalesce(s.store_name, p.full_name)                         as customer_name,
    case when c.store_id is null then 'Pessoa física' else 'Revenda' end as customer_type,
    p.full_name                                                 as contact_name,
    c.territory_id
from customers c
left join persons p on p.person_id = c.person_id
left join stores s on s.store_id = c.store_id
