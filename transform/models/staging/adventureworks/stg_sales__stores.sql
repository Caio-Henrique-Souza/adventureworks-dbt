with source as (
    select * from {{ source('raw_sales', 'Store') }}
)

select
    cast(BusinessEntityID as integer)   as store_id,
    trim(Name)                          as store_name,
    cast(SalesPersonID as integer)      as sales_person_id
from source
