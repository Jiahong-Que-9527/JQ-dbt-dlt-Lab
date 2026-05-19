{% snapshot snp_currencies %}

{{
    config(
        target_schema='snapshots',
        unique_key='currency_code',
        strategy='check',
        check_cols=['currency_name']
    )
}}

select
    code as currency_code,
    name as currency_name
from {{ source('raw_ecb', 'currencies_meta') }}

{% endsnapshot %}
