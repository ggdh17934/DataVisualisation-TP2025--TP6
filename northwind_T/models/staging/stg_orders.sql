select
    {{ dbt_utils.generate_surrogate_key(['order_id']) }} as order_pk,
    order_id::bigint as order_id,
    customer_id,
    employee_id::bigint as employee_id,
    nullif(order_date::text, '')::timestamp as order_date,
    nullif(required_date::text, '')::timestamp as required_date,
    nullif(shipped_date::text, '')::timestamp as shipped_date,
    ship_via::bigint as ship_via,
    freight::numeric as freight,
    ship_name,
    ship_address,
    ship_city,
    ship_region,
    ship_postal_code,
    ship_country
from {{ source('staging_dlt', 'orders') }}
