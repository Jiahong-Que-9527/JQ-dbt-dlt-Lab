{# Custom generic test. Usage in a .yml:
       columns:
         - name: rate_date
           tests:
             - no_future_dates
   dbt wraps any macro named `test_<name>` (or under tests/generic/) as a generic test.
   A test passes when the returned query produces zero rows. #}
{% test no_future_dates(model, column_name) %}
    select {{ column_name }}
    from {{ model }}
    where {{ column_name }} > current_date
{% endtest %}
