select
    {{ dbt_utils.generate_surrogate_key(['product_id']) }} as product_pk,
    product_id::bigint as product_id,
    product_name,
    supplier_id::bigint as supplier_id,
    category_id::bigint as category_id,
    quantity_per_unit,
    unit_price::numeric as unit_price,
    units_in_stock::bigint as units_in_stock,
    units_on_order::bigint as units_on_order,
    reorder_level::bigint as reorder_level,
    discontinued
from {{ source('staging_dlt', 'products') }}
