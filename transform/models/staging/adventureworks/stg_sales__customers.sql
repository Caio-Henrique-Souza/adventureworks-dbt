with source as (
    select * from {{ source('raw_sales', 'Customer') }}
)

select
    cast(CustomerID as integer)     as customer_id,
    cast(PersonID as integer)       as person_id,
    cast(StoreID as integer)        as store_id,
    cast(TerritoryID as integer)    as territory_id,
    AccountNumber                   as account_number
from source
