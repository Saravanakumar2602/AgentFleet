import os
import sys
import uuid
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from sqlalchemy import text

# Traverse up 4 levels to reach the workspace root (AgentFleet/)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from backend.app.database.supabase import SessionLocal
from backend.app.workflows.delivery_workflow import DeliveryWorkflow
from backend.app.registry.registry import get_agent
from backend.app.shared.exceptions import VehicleUnavailableException, InvalidCoordinateException, AgentFleetException

def create_mock_delivery_data(db: Session):
    print("Setting up temporary mock vehicle, driver, and location details for Delivery Workflow test...")
    
    unique_email = f"workflow_driver_{uuid.uuid4().hex[:6]}@agentfleet.com"
    unique_license = f"LIC-WF-{uuid.uuid4().hex[:4].upper()}"
    unique_vehicle = f"KA-WF-{uuid.uuid4().hex[:4].upper()}"
    
    # 1. Insert User (Name: Ravi)
    user_query = text("""
        INSERT INTO users (name, email, password_hash, role)
        VALUES ('Ravi', :email, 'hashedpassword', 'Driver')
        RETURNING id
    """)
    user_id = db.execute(user_query, {"email": unique_email}).scalar()
    
    # 2. Insert Driver
    driver_query = text("""
        INSERT INTO drivers (user_id, license_number, phone, experience_years, status, rating)
        VALUES (:user_id, :license, '+919999988883', 6, 'Available', 4.9)
        RETURNING id
    """)
    driver_id = db.execute(driver_query, {"user_id": user_id, "license": unique_license}).scalar()
    
    # 3. Insert Vehicle (capacity 8000 kg, health score 86)
    vehicle_query = text("""
        INSERT INTO vehicles (vehicle_number, vehicle_type, capacity_kg, fuel_type, fuel_level, status, health_score)
        VALUES (:vehicle_number, 'Dry Van', 8000.0, 'Diesel', 80.0, 'Available', 86.0)
        RETURNING id
    """)
    vehicle_id = db.execute(vehicle_query, {"vehicle_number": unique_vehicle}).scalar()
    
    # 4. Insert Location (Bangalore)
    db.execute(text("""
        INSERT INTO vehicle_locations (vehicle_id, latitude, longitude, speed)
        VALUES (:vehicle_id, 12.9715, 77.5945, 0.0)
    """), {"vehicle_id": vehicle_id})
    
    db.flush()
    return vehicle_id, driver_id

def run_tests():
    db = SessionLocal()
    print("Starting integration test for Delivery Workflow Engine...")
    try:
        # Create mock records
        vehicle_id, driver_id = create_mock_delivery_data(db)
        workflow = DeliveryWorkflow()

        # Test Case 1: Successful Execution (All agents succeed end-to-end)
        print("\n[Test 1] Testing successful workflow execution (Chennai -> Coimbatore, weight = 2500 kg)...")
        res1 = workflow.run(
            db=db,
            task_data={
                "pickup": "13.0827,80.2707",
                "destination": "11.0168,76.9558",
                "weight": 2500.0
            }
        )
        print("Test 1 Result:")
        print(f" - Status: {res1['status']}")
        print(f" - Trip ID: {res1.get('trip_id')}")
        print(f" - Vehicle: {res1.get('vehicle', {}).get('vehicle_number')}")
        print(f" - Driver: {res1.get('driver', {}).get('name')}")
        print(f" - Distance: {res1.get('distance_km')} km")
        print(f" - Duration: {res1.get('estimated_duration')}")
        print(f" - Health score: {res1.get('health_score')}")
        print(f" - Utilization: {res1.get('utilization')}%")
        print(f" - Alert msg: '{res1.get('customer_message')}'")

        assert res1["status"] == "success"
        assert res1["trip_id"] is not None
        assert isinstance(res1["driver"]["name"], str) and len(res1["driver"]["name"]) > 0
        assert res1["estimated_duration"] == "6h 58m"
        assert res1["vehicle_status"] == "Healthy"

        # Test Case 2: Dispatch Failure (excessive weight triggers vehicle unavailable)
        print("\n[Test 2] Testing workflow with Dispatch Agent capacity failure (weight = 99999 kg)...")
        res2 = workflow.run(
            db=db,
            task_data={
                "pickup": "13.0827,80.2707",
                "destination": "11.0168,76.9558",
                "weight": 99999.0
            }
        )
        print("Test 2 Result:")
        print(f" - Status: {res2['status']}")
        print(f" - Failed Agent: {res2.get('failed_agent')}")
        print(f" - Reason: {res2.get('reason')}")
        
        assert res2["status"] == "failed"
        assert res2["failed_agent"] == "Dispatch"
        assert "No suitable vehicle" in res2["reason"]

        # Test Case 3: Route Failure (invalid coordinates)
        print("\n[Test 3] Testing workflow with Route Agent validation failure (out-of-bounds coordinates)...")
        res3 = workflow.run(
            db=db,
            task_data={
                "pickup": "95.0,200.0",
                "destination": "11.0168,76.9558",
                "weight": 2500.0
            }
        )
        print("Test 3 Result:")
        print(f" - Status: {res3['status']}")
        print(f" - Failed Agent: {res3.get('failed_agent')}")
        print(f" - Reason: {res3.get('reason')}")

        assert res3["status"] == "failed"
        assert res3["failed_agent"] == "Route"
        assert "Invalid coordinates" in res3["reason"]

        # Test Case 4: Maintenance Failure (Mock maintenance exception)
        print("\n[Test 4] Testing workflow with Maintenance Agent mock exception...")
        maint_agent = get_agent("maintenance")
        with patch.object(maint_agent, "run", side_effect=VehicleUnavailableException("Maintenance check failed.")):
            res4 = workflow.run(
                db=db,
                task_data={
                    "pickup": "13.0827,80.2707",
                    "destination": "11.0168,76.9558",
                    "weight": 2500.0
                }
            )
            print("Test 4 Result:")
            print(f" - Status: {res4['status']}")
            print(f" - Failed Agent: {res4.get('failed_agent')}")
            print(f" - Reason: {res4.get('reason')}")

            assert res4["status"] == "failed"
            assert res4["failed_agent"] == "Maintenance"
            assert res4["reason"] == "Maintenance check failed."

        # Test Case 5: Analytics Failure (Mock analytics exception)
        print("\n[Test 5] Testing workflow with Analytics Agent mock exception...")
        analytics_agent = get_agent("analytics")
        with patch.object(analytics_agent, "run", side_effect=VehicleUnavailableException("Analytics report failed.")):
            res5 = workflow.run(
                db=db,
                task_data={
                    "pickup": "13.0827,80.2707",
                    "destination": "11.0168,76.9558",
                    "weight": 2500.0
                }
            )
            print("Test 5 Result:")
            print(f" - Status: {res5['status']}")
            print(f" - Failed Agent: {res5.get('failed_agent')}")
            print(f" - Reason: {res5.get('reason')}")

            assert res5["status"] == "failed"
            assert res5["failed_agent"] == "Analytics"
            assert res5["reason"] == "Analytics report failed."

        # Test Case 6: Customer Failure (Mock customer exception)
        print("\n[Test 6] Testing workflow with Customer Agent mock exception...")
        customer_agent = get_agent("customer")
        with patch.object(customer_agent, "run", side_effect=AgentFleetException("Customer notification failed.")):
            res6 = workflow.run(
                db=db,
                task_data={
                    "pickup": "13.0827,80.2707",
                    "destination": "11.0168,76.9558",
                    "weight": 2500.0
                }
            )
            print("Test 6 Result:")
            print(f" - Status: {res6['status']}")
            print(f" - Failed Agent: {res6.get('failed_agent')}")
            print(f" - Reason: {res6.get('reason')}")

            assert res6["status"] == "failed"
            assert res6["failed_agent"] == "Customer"
            assert res6["reason"] == "Customer notification failed."

        print("\nAll Delivery Workflow tests executed successfully. Rolling back database changes.")
    except Exception as e:
        print(f"\n[ERROR] Test Execution Failed: {e}")
        db.rollback()
        raise e
    finally:
        db.rollback()
        db.close()

if __name__ == "__main__":
    run_tests()
