with source as (
    select * from {{ source('raw_sales', 'SalesOrderHeader') }}
)

select
    cast(SalesOrderID as integer)                   as sales_order_id,
    SalesOrderNumber                                as sales_order_number,
    {{ to_date('OrderDate') }}                      as order_date,
    {{ to_date('DueDate') }}                        as due_date,
    {{ to_date('ShipDate') }}                       as ship_date,
    cast(Status as integer)                         as status_code,
    case cast(Status as integer)
        when 1 then 'Em processamento'
        when 2 then 'Aprovado'
        when 3 then 'Em espera'
        when 4 then 'Rejeitado'
        when 5 then 'Enviado'
        when 6 then 'Cancelado'
    end                                             as status,
    OnlineOrderFlag = '1'                           as is_online_order,
    PurchaseOrderNumber                             as purchase_order_number,
    cast(CustomerID as integer)                     as customer_id,
    cast(SalesPersonID as integer)                  as sales_person_id,
    cast(TerritoryID as integer)                    as territory_id,
    cast(BillToAddressID as integer)                as bill_to_address_id,
    cast(ShipToAddressID as integer)                as ship_to_address_id,
    cast(ShipMethodID as integer)                   as ship_method_id,
    cast(SubTotal as decimal(19, 4))                as subtotal,
    cast(TaxAmt as decimal(19, 4))                  as tax_amount,
    cast(Freight as decimal(19, 4))                 as freight,
    cast(SubTotal as decimal(19, 4))
      + cast(TaxAmt as decimal(19, 4))
      + cast(Freight as decimal(19, 4))             as total_due,
    cast(ModifiedDate as timestamp)                 as modified_at
from source
