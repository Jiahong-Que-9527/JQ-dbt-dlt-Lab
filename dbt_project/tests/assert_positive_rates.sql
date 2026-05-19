-- Singular test: ad-hoc SELECT that must return zero rows to pass.
-- Lives at tests/<name>.sql (not under tests/generic/). Use these for one-off
-- business invariants that don't justify a reusable generic test.
select rate_date, currency, rate
from {{ ref('fct_daily_rates') }}
where rate is not null
  and rate <= 0
