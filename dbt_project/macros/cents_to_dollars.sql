{# Example user macro: tiny, reusable, well-named. Production macros tend to be
   thin wrappers around dialect-specific SQL or repeated transformations. #}
{% macro cents_to_dollars(column_name, precision=2) %}
    round( ({{ column_name }} / 100.0)::numeric, {{ precision }} )
{% endmacro %}
