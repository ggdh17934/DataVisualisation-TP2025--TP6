select
    {{ dbt_utils.generate_surrogate_key(['category_id']) }} as category_pk,
    category_id::bigint as category_id,
    category_name,
    description
from {{ source('staging_dlt', 'categories') }}
