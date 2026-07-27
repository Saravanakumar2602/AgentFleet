import os
import sys
import uuid

# Ensure backend package is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.database.supabase import SessionLocal
from backend.app.agents.dispatch.service import DispatchService

def create_mock_data(db: Session):
    print("Inserting temporary mock data for driver, vehicle, and location...")
    
    # Generate unique email to prevent unique constraint failures
    unique_email = f"speedy_{uuid.uuid4().hex[:6]}@agentfleet.com"
    unique_license = f"LIC-{uuid.uuid4().hex[:6].upper()}-TX"
    unique_vehicle = f"KA-01-AF-{uuid.uuid4().hex[:4].upper()}"

    # 1. Insert mock user
    user_query = text("""
        INSERT INTO users (name, email, password_hash, role)
        VALUES ('Speedy Gonzales', :email, 'hashedpassword', 'Driver')
        RETURNING id
    """)
    user_id = db.execute(user_query, {"email": unique_email}).scalar()
    
    # 2. Insert mock driver
    driver_query = text("""
        INSERT INTO drivers (user_id, license_number, phone, experience_years, status, rating)
        VALUES (:user_id, :license, '+919876543210', 8, 'Available', 4.95)
        RETURNING id
    """)
    driver_id = db.execute(driver_query, {"user_id": user_id, "license": unique_license}).scalar()
    
    # 3. Insert mock vehicle
    vehicle_query = text("""
        INSERT INTO vehicles (vehicle_number, vehicle_type, capacity_kg, fuel_type, fuel_level, status, health_score)
        VALUES (:vehicle_number, 'Heavy Duty Reefer', 8000.0, 'Diesel', 100.0, 'Available', 98.5)
        RETURNING id
    """)
    vehicle_id = db.execute(vehicle_query, {"vehicle_number": unique_vehicle}).scalar()
    
    # 4. Insert mock location (Bangalore coordinates)
    location_query = text("""
        INSERT INTO vehicle_locations (vehicle_id, latitude, longitude, speed)
        VALUES (:vehicle_id, 12.9715987, 77.5945627, 0.0)
    """)
    db.execute(location_query, {"vehicle_id": vehicle_id})
    
    db.flush()
    return user_id, driver_id, vehicle_id

def test_dispatch():
    db = SessionLocal()
    print("Starting integration test for Dispatch & Allocation Agent...")
    try:
        # Create mock entities
        user_id, driver_id, vehicle_id = create_mock_data(db)
        
        # Initialize Service
        service = DispatchService()
        
        # Test Case 1: Coordinate-based matching (12.9715, 77.5945)
        print("\n[Test 1] Testing coordinate-based allocation (weight = 2500 kg)...")
        result = service.allocate_dispatch(
            db=db,
            pickup="12.9715,77.5945",
            destination="12.9820,77.6010",
            cargo_weight=2500.0
        )
        print("Test 1 Success! Match result:")
        print(f" - Trip ID: {result['trip_id']}")
        print(f" - Vehicle: {result['vehicle']['vehicle_number']} (ID: {result['vehicle']['id']})")
        print(f" - Driver: {result['driver']['name']} (ID: {result['driver']['id']})")
        
        # Check database statuses after assignment
        v_status = db.execute(text("SELECT status FROM vehicles WHERE id = :id"), {"id": vehicle_id}).scalar()
        d_status = db.execute(text("SELECT status FROM drivers WHERE id = :id"), {"id": driver_id}).scalar()
        print(f"Post-Allocation States in DB: Vehicle status = {v_status}, Driver status = {d_status}")
        
        assert v_status == "Busy"
        assert d_status == "Busy"
        
        print("\nTest executed successfully. Rolling back database changes to preserve state.")
    except Exception as e:
        print(f"\n[ERROR] Test Failed: {e}")
        db.rollback()
        raise e
    finally:
        db.rollback()
        db.close()

if __name__ == "__main__":
    test_dispatch()
