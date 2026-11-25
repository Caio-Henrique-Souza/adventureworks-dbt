{#- Converte o texto de data/hora da Adventure Works ('2022-05-30 00:00:00.000') em DATE. -#}
{% macro to_date(column) -%}
    cast(cast({{ column }} as timestamp) as date)
{%- endmacro %}
