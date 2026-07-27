import os
import sys
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import text

# Traverse up 4 levels to reach the workspace root (AgentFleet/)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from backend.app.database.supabase import SessionLocal
from backend.app.registry.registry import get_agent
from backend.app.shared.exceptions import AgentFleetException

def create_mock_trip_data(db: Session):
    print("Setting up temporary mock vehicle, driver, and trip details for Customer Agent test...")
    
    unique_email = f"customer_driver_{uuid.uuid4().hex[:6]}@agentfleet.com"
    unique_license = f"LIC-CS-{uuid.uuid4().hex[:4].upper()}"
    unique_vehicle = f"KA-CS-{uuid.uuid4().hex[:4].upper()}"
    
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
        VALUES (:user_id, :license, '+919999988884', 6, 'Available', 4.9)
        RETURNING id
    """)
    driver_id = db.execute(driver_query, {"user_id": user_id, "license": unique_license}).scalar()
    
    # 3. Insert Vehicle
    vehicle_query = text("""
        INSERT INTO vehicles (vehicle_number, vehicle_type, capacity_kg, fuel_type, fuel_level, status, health_score)
        VALUES (:vehicle_number, 'Dry Van', 6000.0, 'Diesel', 80.0, 'Available', 95.0)
        RETURNING id
    """)
    vehicle_id = db.execute(vehicle_query, {"vehicle_number": unique_vehicle}).scalar()
    
    # 4. Insert Location
    db.execute(text("""
        INSERT INTO vehicle_locations (vehicle_id, latitude, longitude, speed)
        VALUES (:vehicle_id, 13.0827, 80.2707, 0.0)
    """), {"vehicle_id": vehicle_id})
    
    # 5. Insert Trip (duration: 418 minutes = 6h 58m)
    trip_query = text("""
        INSERT INTO trips (vehicle_id, driver_id, source, destination, distance_km, estimated_duration, status, created_at)
        VALUES (:vehicle_id, :driver_id, 'Chennai', 'Coimbatore', 427.4, 418, 'Assigned', NOW())
        RETURNING id
    """)
    trip_id = db.execute(
        trip_query,
        {
            "vehicle_id": vehicle_id,
            "driver_id": driver_id
        }
    ).scalar()
    
    db.flush()
    return trip_id

def run_tests():
    db = SessionLocal()
    print("Starting integration test for Customer Communication Agent...")
    try:
        # Create mock records
        trip_id = create_mock_trip_data(db)
        agent = get_agent("customer")

        # Test Case 1: Trip Exists and Formats Correctly
        print("\n[Test 1] Testing customer notification trigger on valid trip...")
        res = agent.run(db, {"trip_id": str(trip_id)})
        print("Test 1 Result:")
        print(f" - Status: {res['status']}")
        print(f" - Message: '{res['customer_message']}'")
        print(f" - Type: {res['notification_type']}")
        
        assert res["status"] == "success"
        assert res["trip_id"] == str(trip_id)
        assert res["customer_message"] == "Your shipment has been dispatched. Driver Ravi is on the way. ETA: 6h 58m."
        assert res["notification_type"] == "Trip Update"

        # Test Case 2: Notification Inserted in database table
        print("\n[Test 2] Verifying notification record exists in Supabase table...")
        notif_row = db.execute(
            text("SELECT message, notification_type, status FROM notifications WHERE trip_id = :id"),
            {"id": trip_id}
        ).mappings().first()
        
        print(f"DB Check: message='{notif_row['message']}', type='{notif_row['notification_type']}', status='{notif_row['status']}'")
        assert notif_row["message"] == "Your shipment has been dispatched. Driver Ravi is on the way. ETA: 6h 58m."
        assert notif_row["notification_type"] == "Dispatch_Notice"  # Allowed check constraint code
        assert notif_row["status"] == "Sent"

        # Test Case 3: Trip Missing
        print("\n[Test 3] Testing notification lookup with non-existent trip ID...")
        fake_uuid = str(uuid.uuid4())
        try:
            agent.run(db, {"trip_id": fake_uuid})
            print("❌ Test 3 Failed: Non-existent trip ID did not raise exception.")
            assert False
        except AgentFleetException as e:
            print("Test 3 Success! Correctly raised AgentFleetException.")
            assert e.message == "Trip not found."
            assert e.status_code == 400

        print("\nAll Customer Agent tests executed successfully. Rolling back database changes.")
    except Exception as e:
        print(f"\n[ERROR] Test Execution Failed: {e}")
        db.rollback()
        raise e
    finally:
        db.rollback()
        db.close()

if __name__ == "__main__":
    run_tests()
