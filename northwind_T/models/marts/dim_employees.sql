select *, first_name || ' ' || last_name as employee_full_name
from {{ ref('stg_employees') }}
