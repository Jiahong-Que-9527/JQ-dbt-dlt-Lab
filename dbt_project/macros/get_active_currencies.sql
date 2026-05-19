{# A macro that runs a query at parse time (statement -> run_query) and returns a list.
   Useful when you want to drive Jinja control flow with data from the warehouse,
   e.g. building pivot columns dynamically. #}
{% macro get_active_currencies() %}
  {% if execute %}
    {% set query %}
      select distinct currency
      from {{ ref('stg_ecb_rates') }}
      order by 1
    {% endset %}
    {% set results = run_query(query) %}
    {% set values = results.columns[0].values() | list %}
    {{ return(values) }}
  {% else %}
    {{ return([]) }}
  {% endif %}
{% endmacro %}
