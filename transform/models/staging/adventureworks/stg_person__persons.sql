with source as (
    select * from {{ source('raw_person', 'Person') }}
)

select
    cast(BusinessEntityID as integer)                   as person_id,
    trim(PersonType)                                    as person_type,
    trim(FirstName)                                     as first_name,
    trim(MiddleName)                                    as middle_name,
    trim(LastName)                                      as last_name,
    concat_ws(' ', trim(FirstName), trim(LastName))     as full_name,
    cast(EmailPromotion as integer)                     as email_promotion
from source
