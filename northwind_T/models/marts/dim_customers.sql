with first_orders as (
    select customer_id, min(order_date) as first_order_date
    from {{ ref('stg_orders') }} group by customer_id
)
select c.*, o.first_order_date,
       concat_ws(', ', c.address, c.city, c.region, c.country) as customer_full_address
from {{ ref('stg_customers') }} c
left join first_orders o on c.customer_id = o.customer_id
