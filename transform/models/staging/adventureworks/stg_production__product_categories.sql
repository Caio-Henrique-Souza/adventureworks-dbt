with source as (
    select * from {{ source('raw_production', 'ProductCategory') }}
)

select
    cast(ProductCategoryID as integer)  as product_category_id,
    trim(Name)                          as product_category_name
from source
