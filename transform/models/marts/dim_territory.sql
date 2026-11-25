with territories as (
    select * from {{ ref('stg_sales__territories') }}
),

countries as (
    select * from {{ ref('stg_person__country_regions') }}
)

select
    t.territory_id,
    t.territory_name,
    t.territory_group,
    t.country_region_code,
    c.country_region_name
from territories t
left join countries c on c.country_region_code = t.country_region_code
