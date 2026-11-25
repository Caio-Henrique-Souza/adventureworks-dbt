with source as (
    select * from {{ source('raw_excel', 'metas_vendas') }}
)

select
    make_date(cast(ano as integer), cast(mes as integer), 1)   as target_month,
    trim(territorio)                                           as territory_name,
    cast(meta_usd as decimal(19, 2))                           as target_amount,
    trim(responsavel)                                          as owner_name,
    _source_file                                               as source_file
from source
