with source as (
    select * from {{ source('raw_production', 'ProductModel') }}
)

select
    cast(ProductModelID as integer)     as product_model_id,
    trim(Name)                          as product_model_name
from source
