with source as (
    select * from {{ source('raw_person', 'StateProvince') }}
)

select
    cast(StateProvinceID as integer)    as state_province_id,
    trim(StateProvinceCode)             as state_province_code,
    trim(CountryRegionCode)             as country_region_code,
    trim(Name)                          as state_province_name,
    cast(TerritoryID as integer)        as territory_id
from source
