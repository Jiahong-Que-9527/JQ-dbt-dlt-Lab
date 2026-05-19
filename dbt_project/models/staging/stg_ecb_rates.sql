-- Staging model: cast types and expose dlt metadata from raw_ecb.daily_rates
select
    date::date                as rate_date,
    currency,
    rate::double              as rate,
    _dlt_load_id              as loaded_at_load_id
from {{ source('raw_ecb', 'daily_rates') }}
