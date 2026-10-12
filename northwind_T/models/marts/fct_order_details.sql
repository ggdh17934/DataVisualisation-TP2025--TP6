select d.order_detail_pk, o.order_pk, p.product_pk, c.customer_pk, e.employee_pk,
       d.order_id, d.product_id, d.unit_price, d.quantity, d.discount,
       d.unit_price * d.quantity * (1 - d.discount) as extended_price,
       o.order_date::date as order_date, o.required_date::date as required_date,
       o.shipped_date::date as shipped_date,
       extract(epoch from (o.shipped_date - o.order_date)) / 86400.0 as shipping_delay_days
from {{ ref('stg_order_details') }} d
left join {{ ref('stg_orders') }} o on d.order_id = o.order_id
left join {{ ref('dim_products') }} p on d.product_id = p.product_id
left join {{ ref('dim_customers') }} c on o.customer_id = c.customer_id
left join {{ ref('dim_employees') }} e on o.employee_id = e.employee_id
