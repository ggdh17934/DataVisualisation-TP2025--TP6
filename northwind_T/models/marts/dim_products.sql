select p.*, c.category_name, s.company_name as supplier_name
from {{ ref('stg_products') }} p
left join {{ ref('stg_categories') }} c on p.category_id = c.category_id
left join {{ ref('stg_suppliers') }} s on p.supplier_id = s.supplier_id
