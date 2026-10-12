select
    {{ dbt_utils.generate_surrogate_key(['order_id', 'product_id']) }} as order_detail_pk,
    order_id::bigint as order_id,
    product_id::bigint as product_id,
    unit_price::numeric as unit_price,
    quantity::bigint as quantity,
    discount::numeric as discount
from {{ source('staging_dlt', 'order_details') }}
