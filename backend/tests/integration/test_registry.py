import os
import sys
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import text

# Traverse up 4 levels to reach the workspace root (AgentFleet/)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from backend.app.database.supabase import SessionLocal
from backend.app.registry.registry import get_agent, AGENT_REGISTRY
from backend.app.core.base_agent import BaseAgent
from backend.app.agents.dispatch.agent import DispatchAgent
from backend.app.agents.route.agent import RouteAgent
from backend.app.agents.maintenance.agent import MaintenanceAgent
from backend.app.agents.analytics.agent import AnalyticsAgent

def create_mock_dispatch_data(db: Session):
    print("Setting up temporary mock vehicle/driver data for Dispatch run check...")
    unique_email = f"base_driver_{uuid.uuid4().hex[:6]}@agentfleet.com"
    unique_license = f"LIC-BS-{uuid.uuid4().hex[:4].upper()}"
    unique_vehicle = f"KA-BS-{uuid.uuid4().hex[:4].upper()}"

    # 1. Insert User
    user_id = db.execute(text("""
        INSERT INTO users (name, email, password_hash, role)
        VALUES ('Base Test Driver', :email, 'hashedpassword', 'Driver')
        RETURNING id
    """), {"email": unique_email}).scalar()
    
    # 2. Insert Driver
    driver_id = db.execute(text("""
        INSERT INTO drivers (user_id, license_number, phone, experience_years, status, rating)
        VALUES (:user_id, :license, '+919999988889', 5, 'Available', 4.8)
        RETURNING id
    """), {"user_id": user_id, "license": unique_license}).scalar()
    
    # 3. Insert Vehicle
    vehicle_id = db.execute(text("""
        INSERT INTO vehicles (vehicle_number, vehicle_type, capacity_kg, fuel_type, fuel_level, status, health_score)
        VALUES (:vehicle_number, 'Heavy Reefer', 8000.0, 'Diesel', 100.0, 'Available', 95.0)
        RETURNING id
    """), {"vehicle_number": unique_vehicle}).scalar()
    
    # 4. Insert Location
    db.execute(text("""
        INSERT INTO vehicle_locations (vehicle_id, latitude, longitude, speed)
        VALUES (:vehicle_id, 12.9715, 77.5945, 0.0)
    """), {"vehicle_id": vehicle_id})
    
    db.flush()
    return vehicle_id, driver_id

def run_tests():
    db = SessionLocal()
    print("Starting integration test for Agent Registry & BaseAgent inheritance...")
    try:
        # Test Case 1: Registry returns correct agents
        print("\n[Test 1] Testing registry retrieval helpers...")
        dispatch_agent = get_agent("dispatch")
        route_agent = get_agent("route")
        maint_agent = get_agent("maintenance")
        analytics_agent = get_agent("analytics")

        assert isinstance(dispatch_agent, DispatchAgent)
        assert isinstance(route_agent, RouteAgent)
        assert isinstance(maint_agent, MaintenanceAgent)
        assert isinstance(analytics_agent, AnalyticsAgent)
        print("Test 1 Success! Registry returns correct concrete types.")

        # Test Case 2: BaseAgent inheritance works
        print("\n[Test 2] Testing BaseAgent class inheritance...")
        assert isinstance(dispatch_agent, BaseAgent)
        assert isinstance(route_agent, BaseAgent)
        assert isinstance(maint_agent, BaseAgent)
        assert isinstance(analytics_agent, BaseAgent)
        print("Test 2 Success! All agents correctly inherit from BaseAgent.")

        # Test Case 3: run() executes successfully
        print("\n[Test 3] Testing orchestrator run() hook execution on DispatchAgent...")
        create_mock_dispatch_data(db)
        
        task_inputs = {
            "pickup": "12.9715,77.5945",
            "destination": "12.9820,77.6010",
            "weight": 2500.0
        }
        
        response = dispatch_agent.run(db, task_inputs)
        print("Test 3 Success! Result:")
        print(f" - Status: {response['status']}")
        print(f" - Agent: {response['agent']}")
        print(f" - Trip ID: {response['trip_id']}")
        print(f" - Vehicle: {response['vehicle']['vehicle_number']}")
        print(f" - Driver: {response['driver']['name']}")

        assert response["status"] == "success"
        assert response["agent"] == "Dispatch Agent"
        assert response["trip_id"] is not None

        # Test Case 4: run() validation check raises error
        print("\n[Test 4] Testing orchestrator validation checking raises exception on missing keys...")
        bad_inputs = {"pickup": "12.9715,77.5945"}
        try:
            dispatch_agent.run(db, bad_inputs)
            print("❌ Test 4 Failed: Validation mismatch did not raise ValueError.")
            assert False
        except ValueError:
            print("Test 4 Success! Correctly raised ValueError on validation checks.")

        print("\nAll Registry and BaseAgent tests executed successfully. Rolling back changes.")
    except Exception as e:
        print(f"\n[ERROR] Test Execution Failed: {e}")
        db.rollback()
        raise e
    finally:
        db.rollback()
        db.close()

if __name__ == "__main__":
    run_tests()
