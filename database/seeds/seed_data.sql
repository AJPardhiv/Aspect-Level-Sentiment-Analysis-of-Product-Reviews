-- Seed Staff Data
INSERT INTO staff (name, role, availability_date, is_available, hourly_rate)
VALUES
  ('Chef Raj', 'cook', '2026-04-15', TRUE, 75.00),
  ('Chef Priya', 'cook', '2026-04-15', TRUE, 70.00),
  ('Chef Amit', 'cook', '2026-04-16', TRUE, 65.00),
  ('Helper Ravi', 'helper', '2026-04-15', TRUE, 25.00),
  ('Helper Sunita', 'helper', '2026-04-15', TRUE, 25.00),
  ('Helper Kumar', 'helper', '2026-04-16', TRUE, 23.00),
  ('Server John', 'server', '2026-04-15', TRUE, 20.00),
  ('Server Sarah', 'server', '2026-04-15', TRUE, 20.00),
  ('Server Mike', 'server', '2026-04-16', TRUE, 22.00);

-- Seed Inventory Data
INSERT INTO inventory (name, category, quantity_available, unit, cost_per_unit, reorder_level)
VALUES
  ('Chicken Breast', 'protein', 50, 'kg', 8.50, 10),
  ('Paneer', 'protein', 30, 'kg', 12.00, 5),
  ('Rice', 'grain', 100, 'kg', 2.00, 20),
  ('Dal', 'legume', 40, 'kg', 3.50, 10),
  ('Onions', 'vegetable', 80, 'kg', 1.50, 15),
  ('Garlic', 'vegetable', 25, 'kg', 5.00, 5),
  ('Ginger', 'vegetable', 20, 'kg', 6.00, 5),
  ('Tomatoes', 'vegetable', 60, 'kg', 2.50, 15),
  ('Bell Peppers', 'vegetable', 40, 'kg', 4.00, 10),
  ('Flour', 'grain', 50, 'kg', 1.75, 10),
  ('Oil', 'condiment', 30, 'liter', 8.00, 5),
  ('Salt', 'condiment', 10, 'kg', 0.50, 2),
  ('Sugar', 'condiment', 15, 'kg', 1.20, 5),
  ('Turmeric', 'spice', 5, 'kg', 15.00, 1),
  ('Red Chili Powder', 'spice', 5, 'kg', 12.00, 1),
  ('Cumin Seeds', 'spice', 3, 'kg', 18.00, 1),
  ('Hari Cilantro', 'herb', 10, 'kg', 3.00, 2);
