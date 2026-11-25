with source as (
    select * from {{ source('raw_production', 'Product') }}
)

select
    cast(ProductID as integer)              as product_id,
    trim(Name)                              as product_name,
    trim(ProductNumber)                     as product_number,
    FinishedGoodsFlag = '1'                 as is_finished_good,
    trim(Color)                             as color,
    trim(Size)                              as size,
    case trim(ProductLine)
        when 'R' then 'Road'
        when 'M' then 'Mountain'
        when 'T' then 'Touring'
        when 'S' then 'Standard'
    end                                     as product_line,
    trim(Class)                             as class,
    trim(Style)                             as style,
    cast(StandardCost as decimal(19, 4))    as standard_cost,
    cast(ListPrice as decimal(19, 4))       as list_price,
    cast(ProductSubcategoryID as integer)   as product_subcategory_id,
    cast(ProductModelID as integer)         as product_model_id,
    {{ to_date('SellStartDate') }}          as sell_start_date,
    {{ to_date('SellEndDate') }}            as sell_end_date,
    {{ to_date('DiscontinuedDate') }}       as discontinued_date
from source
