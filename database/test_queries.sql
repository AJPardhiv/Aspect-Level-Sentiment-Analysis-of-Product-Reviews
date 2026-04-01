-- Test Data Examples
-- Use these queries to verify the system is working

-- 1. View all staff
SELECT 
    id, name, role, availability_date, hourly_rate 
FROM staff 
ORDER BY role, hourly_rate DESC;

-- 2. View inventory levels
SELECT 
    name, category, quantity_available, unit, cost_per_unit 
FROM inventory 
ORDER BY category;

-- 3. Check recent events
SELECT 
    id, name, guest_count, menu_type, event_date, status, created_at 
FROM events 
ORDER BY created_at DESC 
LIMIT 10;

-- 4. Get event execution logs
-- Replace 'YOUR_EVENT_ID' with actual event UUID
SELECT 
    step, status, message, created_at 
FROM execution_logs 
WHERE event_id = 'YOUR_EVENT_ID'
ORDER BY created_at ASC;

-- 5. View staff assignments for an event
-- Replace 'YOUR_EVENT_ID' with actual event UUID
SELECT 
    s.name, 
    esa.role, 
    esa.start_time, 
    esa.end_time, 
    esa.cost 
FROM event_staff_assignments esa
JOIN staff s ON esa.staff_id = s.id
WHERE esa.event_id = 'YOUR_EVENT_ID';

-- 6. Get event plan details
-- Replace 'YOUR_EVENT_ID' with actual event UUID
SELECT 
    id, 
    event_id,
    status,
    plan_data,
    created_at 
FROM plans 
WHERE event_id = 'YOUR_EVENT_ID' 
ORDER BY created_at DESC 
LIMIT 1;

-- Example workflow test query:
-- Copy this output to verify the workflow data structure
EXPLAIN (FORMAT JSON) 
SELECT 
    e.id,
    e.name,
    e.guest_count,
    e.menu_type,
    p.plan_data 
FROM events e 
LEFT JOIN plans p ON e.id = p.event_id;
