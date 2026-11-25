with source as (
    select * from {{ source('raw_person', 'CountryRegion') }}
)

select
    trim(CountryRegionCode)     as country_region_code,
    trim(Name)                  as country_region_name
from source
