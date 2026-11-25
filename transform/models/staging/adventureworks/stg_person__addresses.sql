with source as (
    select * from {{ source('raw_person', 'Address') }}
)

select
    cast(AddressID as integer)          as address_id,
    trim(AddressLine1)                  as address_line_1,
    trim(City)                          as city,
    cast(StateProvinceID as integer)    as state_province_id,
    trim(PostalCode)                    as postal_code
from source
