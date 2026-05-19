with stg as (
    select * from {{ ref('stg_ecb_rates') }}
),
dim as (
    select * from {{ ref('dim_currencies') }}
)
select
    stg.rate_date,
    stg.currency,
    dim.currency_name,
    stg.rate,
    (
        stg.rate - lag(stg.rate) over (partition by stg.currency order by stg.rate_date)
    ) / nullif(
        lag(stg.rate) over (partition by stg.currency order by stg.rate_date),
        0
    ) as rate_change_pct
from stg
join dim on stg.currency = dim.currency_code
