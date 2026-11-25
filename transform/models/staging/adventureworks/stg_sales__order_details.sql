with source as (
    select * from {{ source('raw_sales', 'SalesOrderDetail') }}
)

select
    cast(SalesOrderDetailID as integer)             as sales_order_detail_id,
    cast(SalesOrderID as integer)                   as sales_order_id,
    cast(ProductID as integer)                      as product_id,
    cast(SpecialOfferID as integer)                 as special_offer_id,
    cast(OrderQty as integer)                       as order_qty,
    cast(UnitPrice as decimal(19, 4))               as unit_price,
    cast(UnitPriceDiscount as decimal(9, 4))        as unit_price_discount,
    cast(LineTotal as decimal(19, 4))               as line_total,
    CarrierTrackingNumber                           as carrier_tracking_number,
    cast(ModifiedDate as timestamp)                 as modified_at
from source
