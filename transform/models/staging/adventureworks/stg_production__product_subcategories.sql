with source as (
    select * from {{ source('raw_production', 'ProductSubcategory') }}
)

select
    cast(ProductSubcategoryID as integer)   as product_subcategory_id,
    cast(ProductCategoryID as integer)      as product_category_id,
    trim(Name)                              as product_subcategory_name
from source
