with source as (
    select * from {{ source('raw_sales', 'SalesTerritory') }}
)

select
    cast(TerritoryID as integer)    as territory_id,
    trim(Name)                      as territory_name,
    trim(CountryRegionCode)         as country_region_code,
    trim("Group")                   as territory_group
from source
