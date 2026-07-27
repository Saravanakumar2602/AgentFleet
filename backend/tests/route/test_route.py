import os
import sys
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import text

# Traverse up 4 levels to reach the workspace root (AgentFleet/)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from backend.app.database.supabase import SessionLocal
from backend.app.agents.route.service import RouteService
from backend.app.shared.exceptions import InvalidCoordinateException, VehicleUnavailableException

def create_mock_route_data(db: Session):
    print("Setting up temporary mock data for Route Agent test...")
    
    unique_email = f"route_driver_{uuid.uuid4().hex[:6]}@agentfleet.com"
    unique_license = f"LIC-RT-{uuid.uuid4().hex[:4].upper()}"
    unique_vehicle = f"KA-RT-{uuid.uuid4().hex[:4].upper()}"
    
    # 1. Insert User
    user_query = text("""
        INSERT INTO users (name, email, password_hash, role)
        VALUES ('Route Test Driver', :email, 'hashedpassword', 'Driver')
        RETURNING id
    """)
    user_id = db.execute(user_query, {"email": unique_email}).scalar()
    
    # 2. Insert Driver
    driver_query = text("""
        INSERT INTO drivers (user_id, license_number, phone, experience_years, status, rating)
        VALUES (:user_id, :license, '+919999988888', 6, 'Available', 4.8)
        RETURNING id
    """)
    driver_id = db.execute(driver_query, {"user_id": user_id, "license": unique_license}).scalar()
    
    # 3. Insert Vehicle
    vehicle_query = text("""
        INSERT INTO vehicles (vehicle_number, vehicle_type, capacity_kg, fuel_type, fuel_level, status, health_score)
        VALUES (:vehicle_number, 'Reefer Truck', 10000.0, 'Diesel', 90.0, 'Available', 99.0)
        RETURNING id
    """)
    vehicle_id = db.execute(vehicle_query, {"vehicle_number": unique_vehicle}).scalar()
    
    # 4. Insert Location
    location_query = text("""
        INSERT INTO vehicle_locations (vehicle_id, latitude, longitude, speed)
        VALUES (:vehicle_id, 13.0827, 80.2707, 0.0)
    """)
    db.execute(location_query, {"vehicle_id": vehicle_id})
    
    # 5. Insert Trip
    trip_query = text("""
        INSERT INTO trips (vehicle_id, driver_id, source, destination, distance_km, estimated_duration, status, created_at)
        VALUES (:vehicle_id, :driver_id, '13.0827,80.2707', '11.0168,76.9558', 1.0, 10, 'Assigned', NOW())
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
    return vehicle_id, trip_id

def run_tests():
    db = SessionLocal()
    print("Starting integration test for Route Intelligence Agent...")
    try:
        # 1. Setup mock records
        vehicle_id, trip_id = create_mock_route_data(db)
        service = RouteService()

        # Test Case A: Valid coordinates
        print("\n[Test 1] Testing route calculations with valid coordinates (Chennai -> Coimbatore)...")
        result = service.generate_route(
            db=db,
            vehicle_id=str(vehicle_id),
            pickup="13.0827,80.2707",
            destination="11.0168,76.9558"
        )
        print("Test 1 Success! Match result:")
        print(f" - Trip ID: {result['trip_id']}")
        print(f" - Distance: {result['distance_km']} km (Expected: ~427.4)")
        print(f" - Duration: {result['estimated_duration']} (Expected: 6h 58m)")
        print(f" - Fuel liters: {result['estimated_fuel']} L (Expected: ~61.0)")
        
        assert result["trip_id"] == str(trip_id)
        assert abs(result["distance_km"] - 427.4) <= 1.0
        assert result["estimated_duration"] == "6h 58m"
        assert abs(result["estimated_fuel"] - 61.0) <= 1.0

        # Test Case B: Trip update successful in DB state
        print("\n[Test 2] Verifying trip state has updated in Supabase...")
        trip_state = db.execute(
            text("SELECT distance_km, estimated_duration, status FROM trips WHERE id = :id"),
            {"id": trip_id}
        ).mappings().first()
        print(f"Trip state in DB: status = {trip_state['status']}, distance = {trip_state['distance_km']} km, duration = {trip_state['estimated_duration']} mins")
        
        assert trip_state["status"] == "Route Generated"
        assert trip_state["estimated_duration"] == 418 # 6h 58m in minutes

        # Test Case C: Invalid coordinates
        print("\n[Test 3] Testing route with invalid coordinates (out-of-bounds)...")
        try:
            service.generate_route(
                db=db,
                vehicle_id=str(vehicle_id),
                pickup="95.0,200.0",
                destination="11.0168,76.9558"
            )
            print("❌ Test 3 Failed: Invalid coordinates did not raise exception.")
            assert False
        except InvalidCoordinateException:
            print("Test 3 Success! Correctly raised InvalidCoordinateException.")

        # Test Case D: Vehicle not found
        print("\n[Test 4] Testing route with missing vehicle ID...")
        fake_uuid = str(uuid.uuid4())
        try:
            service.generate_route(
                db=db,
                vehicle_id=fake_uuid,
                pickup="13.0827,80.2707",
                destination="11.0168,76.9558"
            )
            print("❌ Test 4 Failed: Fake vehicle ID did not raise exception.")
            assert False
        except VehicleUnavailableException:
            print("Test 4 Success! Correctly raised VehicleUnavailableException.")

        print("\nAll Route Agent tests executed successfully. Rolling back database changes.")
    except Exception as e:
        print(f"\n[ERROR] Test Execution Failed: {e}")
        db.rollback()
        raise e
    finally:
        db.rollback()
        db.close()

if __name__ == "__main__":
    run_tests()
