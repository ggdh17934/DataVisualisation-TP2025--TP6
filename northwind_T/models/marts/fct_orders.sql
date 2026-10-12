with totals as (
    select order_id, sum(unit_price * quantity * (1 - discount)) as total_order_value
    from {{ ref('stg_order_details') }} group by order_id
)
select o.*, c.customer_pk, e.employee_pk, t.total_order_value,
       case when o.shipped_date is not null then 'Shipped' else 'Pending' end as order_status_flag,
       extract(epoch from (o.shipped_date - o.order_date)) / 86400.0 as shipping_delay_days
from {{ ref('stg_orders') }} o
left join totals t on o.order_id = t.order_id
left join {{ ref('dim_customers') }} c on o.customer_id = c.customer_id
left join {{ ref('dim_employees') }} e on o.employee_id = e.employee_id
