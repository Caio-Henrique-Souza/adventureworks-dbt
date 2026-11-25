{#- Teste genérico: a combinação de colunas não pode se repetir (sem depender do pacote dbt_utils). -#}
{% test dbt_utils_free_unique_combination(model, columns) %}
select {{ columns | join(', ') }}, count(*) as ocorrencias
from {{ model }}
group by {{ columns | join(', ') }}
having count(*) > 1
{% endtest %}
