-- Create Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Events Table
CREATE TABLE events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL,
  guest_count INT NOT NULL,
  menu_type VARCHAR(50) NOT NULL CHECK (menu_type IN ('veg', 'non-veg')),
  event_date TIMESTAMP NOT NULL,
  location VARCHAR(255) NOT NULL,
  status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'planning', 'confirmed', 'completed', 'cancelled')),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Staff Table
CREATE TABLE staff (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL,
  role VARCHAR(50) NOT NULL CHECK (role IN ('cook', 'helper', 'server')),
  availability_date DATE NOT NULL,
  is_available BOOLEAN DEFAULT TRUE,
  hourly_rate DECIMAL(8, 2),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inventory Table
CREATE TABLE inventory (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL,
  category VARCHAR(100),
  quantity_available INT NOT NULL,
  unit VARCHAR(50),
  cost_per_unit DECIMAL(8, 2),
  reorder_level INT,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Plans Table
CREATE TABLE plans (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  event_id UUID NOT NULL,
  plan_data JSONB NOT NULL,
  status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'finalized', 'executed', 'cancelled')),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
);

-- Event Staff Assignment Table
CREATE TABLE event_staff_assignments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  event_id UUID NOT NULL,
  staff_id UUID NOT NULL,
  role VARCHAR(50) NOT NULL,
  start_time TIMESTAMP,
  end_time TIMESTAMP,
  cost DECIMAL(10, 2),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
  FOREIGN KEY (staff_id) REFERENCES staff(id) ON DELETE CASCADE
);

-- Execution Logs Table
CREATE TABLE execution_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  event_id UUID NOT NULL,
  step VARCHAR(100) NOT NULL,
  status VARCHAR(50) NOT NULL CHECK (status IN ('pending', 'running', 'completed', 'failed')),
  message TEXT,
  data JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_events_status ON events(status);
CREATE INDEX idx_events_date ON events(event_date);
CREATE INDEX idx_staff_availability ON staff(availability_date, is_available);
CREATE INDEX idx_plans_event_id ON plans(event_id);
CREATE INDEX idx_assignments_event_id ON event_staff_assignments(event_id);
CREATE INDEX idx_logs_event_id ON execution_logs(event_id);
