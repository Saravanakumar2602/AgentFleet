-- ============================================================================
-- Project: AgentFleet - Intelligent Fleet Management System
-- Description: Production-ready database schema compatible with Supabase PostgreSQL (3NF)
-- Targets: PostgreSQL 13+ (Supabase)
-- Author: Senior Database Architect
-- ============================================================================

-- Enable UUID-OSSP extension for UUID generation if needed (Supabase has gen_random_uuid built-in)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 1. Table: users
-- Purpose: System authentication and authorization details for operators/drivers
-- ============================================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CONSTRAINT chk_users_role CHECK (role IN ('Admin', 'Fleet Manager', 'Driver')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Auto-update updated_at timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 2. Table: drivers
-- Purpose: Extended profiles for drivers, referenced by vehicle allocations
-- ============================================================================
CREATE TABLE drivers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    license_number VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(30) NOT NULL,
    experience_years INT NOT NULL CONSTRAINT chk_drivers_experience_years CHECK (experience_years >= 0),
    status VARCHAR(50) NOT NULL DEFAULT 'Available' CONSTRAINT chk_drivers_status CHECK (status IN ('Available', 'Busy', 'Offline')),
    rating DECIMAL(3, 2) CONSTRAINT chk_drivers_rating CHECK (rating >= 0.00 AND rating <= 5.00),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- 3. Table: vehicles
-- Purpose: Details of vehicles in the fleet and their operational statuses
-- ============================================================================
CREATE TABLE vehicles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_number VARCHAR(100) UNIQUE NOT NULL,
    vehicle_type VARCHAR(100) NOT NULL,
    capacity_kg DECIMAL(10, 2) NOT NULL CONSTRAINT chk_vehicles_capacity_kg CHECK (capacity_kg > 0.00),
    fuel_type VARCHAR(50) NOT NULL,
    fuel_level DECIMAL(5, 2) NOT NULL DEFAULT 100.00 CONSTRAINT chk_vehicles_fuel_level CHECK (fuel_level >= 0.00 AND fuel_level <= 100.00),
    status VARCHAR(50) NOT NULL DEFAULT 'Available' CONSTRAINT chk_vehicles_status CHECK (status IN ('Available', 'Busy', 'Maintenance')),
    health_score DECIMAL(5, 2) NOT NULL DEFAULT 100.00 CONSTRAINT chk_vehicles_health_score CHECK (health_score >= 0.00 AND health_score <= 100.00),
    current_driver_id UUID REFERENCES drivers(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- 4. Table: vehicle_locations
-- Purpose: Current real-time coordinates of active vehicles (1-to-1 extension)
-- ============================================================================
CREATE TABLE vehicle_locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id UUID UNIQUE NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    latitude DECIMAL(9, 6) NOT NULL CONSTRAINT chk_locations_latitude CHECK (latitude >= -90.000000 AND latitude <= 90.000000),
    longitude DECIMAL(9, 6) NOT NULL CONSTRAINT chk_locations_longitude CHECK (longitude >= -180.000000 AND longitude <= 180.000000),
    speed DECIMAL(5, 2) NOT NULL CONSTRAINT chk_locations_speed CHECK (speed >= 0.00),
    last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- 5. Table: trips
-- Purpose: Dispatch assignments, routing details, and tracking lifecycle
-- ============================================================================
CREATE TABLE trips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE SET NULL,
    driver_id UUID REFERENCES drivers(id) ON DELETE SET NULL,
    source VARCHAR(255) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    distance_km DECIMAL(8, 2) NOT NULL CONSTRAINT chk_trips_distance_km CHECK (distance_km > 0.00),
    estimated_duration INT NOT NULL CONSTRAINT chk_trips_estimated_duration CHECK (estimated_duration > 0), -- duration in minutes
    status VARCHAR(50) NOT NULL DEFAULT 'Pending' CONSTRAINT chk_trips_status CHECK (status IN ('Pending', 'Assigned', 'In Transit', 'Completed', 'Cancelled')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    CONSTRAINT chk_completed_at CHECK (completed_at IS NULL OR status IN ('Completed', 'Cancelled'))
);

-- ============================================================================
-- 6. Table: maintenance_logs
-- Purpose: Historical logs of repairs, preventative inspections, and DTC flags
-- ============================================================================
CREATE TABLE maintenance_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    issue TEXT NOT NULL,
    health_score DECIMAL(5, 2) CONSTRAINT chk_maintenance_health CHECK (health_score >= 0.00 AND health_score <= 100.00),
    service_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    next_service_date TIMESTAMPTZ,
    status VARCHAR(50) NOT NULL DEFAULT 'Scheduled' CONSTRAINT chk_maintenance_status CHECK (status IN ('Scheduled', 'In Progress', 'Completed', 'Cancelled')),
    CONSTRAINT chk_service_dates CHECK (next_service_date IS NULL OR next_service_date >= service_date)
);

-- ============================================================================
-- 7. Table: analytics
-- Purpose: Aggregated KPIs computed after trip completion for optimization
-- ============================================================================
CREATE TABLE analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID UNIQUE NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    fuel_used DECIMAL(8, 2) CONSTRAINT chk_analytics_fuel CHECK (fuel_used >= 0.00), -- in liters
    average_speed DECIMAL(5, 2) CONSTRAINT chk_analytics_speed CHECK (average_speed >= 0.00), -- in km/h
    cost DECIMAL(10, 2) CONSTRAINT chk_analytics_cost CHECK (cost >= 0.00), -- base currency
    delivery_time INT CONSTRAINT chk_analytics_delivery_time CHECK (delivery_time >= 0), -- actual duration in minutes
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- 8. Table: notifications
-- Purpose: Outbound alerts and updates dispatched to customers or supervisors
-- ============================================================================
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID REFERENCES trips(id) ON DELETE SET NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) NOT NULL CONSTRAINT chk_notifications_type CHECK (notification_type IN ('ETA_Update', 'Delay_Alert', 'Dispatch_Notice', 'Completion_Notice')),
    status VARCHAR(50) NOT NULL DEFAULT 'Pending' CONSTRAINT chk_notifications_status CHECK (status IN ('Pending', 'Sent', 'Failed')),
    sent_at TIMESTAMPTZ
);

-- ============================================================================
-- 9. Table: agent_logs
-- Purpose: Comprehensive audit trail of actions taken by the autonomous AI agents
-- ============================================================================
CREATE TABLE agent_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name VARCHAR(100) NOT NULL CONSTRAINT chk_agent_logs_name CHECK (agent_name IN ('dispatch', 'route', 'maintenance', 'analytics', 'customer', 'supervisor')),
    action TEXT NOT NULL,
    status VARCHAR(50) NOT NULL CONSTRAINT chk_agent_logs_status CHECK (status IN ('Success', 'Failure', 'Running')),
    execution_time_ms INT NOT NULL CONSTRAINT chk_agent_logs_exec_time CHECK (execution_time_ms >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- Index Recommendations for Performance Optimization
-- ============================================================================

-- Foreign Key indexing to optimize join performance
CREATE INDEX idx_drivers_user_id ON drivers(user_id);
CREATE INDEX idx_vehicles_current_driver_id ON vehicles(current_driver_id);
CREATE INDEX idx_trips_vehicle_id ON trips(vehicle_id);
CREATE INDEX idx_trips_driver_id ON trips(driver_id);
CREATE INDEX idx_maintenance_logs_vehicle_id ON maintenance_logs(vehicle_id);
CREATE INDEX idx_notifications_trip_id ON notifications(trip_id);

-- Operational lookup optimization indexes (B-tree)
CREATE INDEX idx_vehicles_status ON vehicles(status);
CREATE INDEX idx_drivers_status ON drivers(status);
CREATE INDEX idx_trips_status ON trips(status);
CREATE INDEX idx_agent_logs_agent_name_created ON agent_logs(agent_name, created_at DESC);
CREATE INDEX idx_vehicle_locations_vehicle_id ON vehicle_locations(vehicle_id);
