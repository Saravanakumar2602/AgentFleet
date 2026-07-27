import os
import sys
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import text

# Traverse up 4 levels to reach the workspace root (AgentFleet/)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from backend.app.database.supabase import SessionLocal
from backend.app.agents.analytics.service import AnalyticsService
from backend.app.shared.exceptions import VehicleUnavailableException

def create_mock_analytics_data(db: Session):
    print("Setting up temporary mock vehicle and trip records for Analytics test...")
    
    unique_email = f"analytics_driver_{uuid.uuid4().hex[:6]}@agentfleet.com"
    unique_license = f"LIC-AN-{uuid.uuid4().hex[:4].upper()}"
    
    # 1. Insert User
    user_query = text("""
        INSERT INTO users (name, email, password_hash, role)
        VALUES ('Analytics Test Driver', :email, 'hashedpassword', 'Driver')
        RETURNING id
    """)
    user_id = db.execute(user_query, {"email": unique_email}).scalar()
    
    # 2. Insert Driver
    driver_query = text("""
        INSERT INTO drivers (user_id, license_number, phone, experience_years, status, rating)
        VALUES (:user_id, :license, '+919999988887', 5, 'Available', 4.7)
        RETURNING id
    """)
    driver_id = db.execute(driver_query, {"user_id": user_id, "license": unique_license}).scalar()
    
    # 3. Create Vehicles
    # Vehicle 1: No trips at all
    v_under_num = f"KA-AN-{uuid.uuid4().hex[:4].upper()}"
    v_under_id = db.execute(text("""
        INSERT INTO vehicles (vehicle_number, vehicle_type, capacity_kg, fuel_type, fuel_level, status, health_score)
        VALUES (:num, 'Flatbed', 6000.0, 'Diesel', 100.0, 'Available', 95.0)
        RETURNING id
    """), {"num": v_under_num}).scalar()
    
    # Vehicle 2: High utilization (42 trips, 13792.8 km, 1839 L fuel)
    v_high_num = f"KA-AF-{uuid.uuid4().hex[:4].upper()}"
    v_high_id = db.execute(text("""
        INSERT INTO vehicles (vehicle_number, vehicle_type, capacity_kg, fuel_type, fuel_level, status, health_score)
        VALUES (:num, 'Heavy Reefer', 8000.0, 'Diesel', 100.0, 'Available', 86.0)
        RETURNING id
    """), {"num": v_high_num}).scalar()
    
    # Insert 42 trips to match total_trips logic
    total_target_distance = 13792.8
    total_target_fuel = 1839.0
    
    # Insert 41 quick trips
    for _ in range(41):
        trip_id = db.execute(text("""
            INSERT INTO trips (vehicle_id, driver_id, source, destination, distance_km, estimated_duration, status)
            VALUES (:v_id, :d_id, 'Source', 'Dest', 1.0, 5, 'Completed')
            RETURNING id
        """), {"v_id": v_high_id, "d_id": driver_id}).scalar()
        
        db.execute(text("""
            INSERT INTO analytics (trip_id, fuel_used, average_speed, cost, delivery_time)
            VALUES (:trip_id, 0.1, 50.0, 10.0, 5)
        """), {"trip_id": trip_id})
        
    # Insert 42nd trip carrying the main distance and fuel balance
    trip_id_42 = db.execute(text("""
        INSERT INTO trips (vehicle_id, driver_id, source, destination, distance_km, estimated_duration, status)
        VALUES (:v_id, :d_id, 'Source', 'Dest', :dist, 400, 'Completed')
        RETURNING id
    """), {"v_id": v_high_id, "d_id": driver_id, "dist": total_target_distance - 41.0}).scalar()
    
    db.execute(text("""
        INSERT INTO analytics (trip_id, fuel_used, average_speed, cost, delivery_time)
        VALUES (:trip_id, :fuel, 50.0, 100.0, 400)
    """), {"trip_id": trip_id_42, "fuel": total_target_fuel - 4.1})
    
    # Vehicle 3: Poor fuel efficiency (yielding 3.5 km/L)
    v_poor_num = f"KA-AN-{uuid.uuid4().hex[:4].upper()}"
    v_poor_id = db.execute(text("""
        INSERT INTO vehicles (vehicle_number, vehicle_type, capacity_kg, fuel_type, fuel_level, status, health_score)
        VALUES (:num, 'Box Truck', 4000.0, 'Gasoline', 100.0, 'Available', 90.0)
        RETURNING id
    """), {"num": v_poor_num}).scalar()
    
    trip_id_poor = db.execute(text("""
        INSERT INTO trips (vehicle_id, driver_id, source, destination, distance_km, estimated_duration, status)
        VALUES (:v_id, :d_id, 'Source', 'Dest', 7000.0, 500, 'Completed')
        RETURNING id
    """), {"v_id": v_poor_id, "d_id": driver_id}).scalar()
    
    db.execute(text("""
        INSERT INTO analytics (trip_id, fuel_used, average_speed, cost, delivery_time)
        VALUES (:trip_id, 2000.0, 50.0, 200.0, 500)
    """), {"trip_id": trip_id_poor})
    
    # Vehicle 4: Frequent maintenance
    v_maint_num = f"KA-AN-{uuid.uuid4().hex[:4].upper()}"
    v_maint_id = db.execute(text("""
        INSERT INTO vehicles (vehicle_number, vehicle_type, capacity_kg, fuel_type, fuel_level, status, health_score)
        VALUES (:num, 'Dry Van', 5000.0, 'Diesel', 100.0, 'Available', 75.0)
        RETURNING id
    """), {"num": v_maint_num}).scalar()
    
    trip_id_maint = db.execute(text("""
        INSERT INTO trips (vehicle_id, driver_id, source, destination, distance_km, estimated_duration, status)
        VALUES (:v_id, :d_id, 'Source', 'Dest', 7000.0, 500, 'Completed')
        RETURNING id
    """), {"v_id": v_maint_id, "d_id": driver_id}).scalar()
    
    db.execute(text("""
        INSERT INTO analytics (trip_id, fuel_used, average_speed, cost, delivery_time)
        VALUES (:trip_id, 900.0, 50.0, 150.0, 500)
    """), {"trip_id": trip_id_maint})
    
    # Insert 6 maintenance logs
    for i in range(6):
        db.execute(text("""
            INSERT INTO maintenance_logs (vehicle_id, issue, health_score, status)
            VALUES (:v_id, :issue, 75.0, 'Completed')
        """), {"v_id": v_maint_id, "issue": f"Regular service check {i+1}"})

    db.flush()
    return v_under_id, v_high_id, v_high_num, v_poor_id, v_maint_id

def run_tests():
    db = SessionLocal()
    print("Starting integration test for Fleet Analytics & Optimization Agent...")
    try:
        # Create mock records
        v_under, v_high, v_high_num, v_poor, v_maint = create_mock_analytics_data(db)
        service = AnalyticsService()

        # Test Case 1: Underutilized Vehicle (0 trips)
        print("\n[Test 1] Testing vehicle with no trips (utilization < 40%)...")
        res1 = service.generate_report(db, str(v_under))
        print("Test 1 Result:")
        print(f" - Trips: {res1['total_trips']}")
        print(f" - Utilization: {res1['utilization']}%")
        print(f" - Fuel efficiency: {res1['fuel_efficiency']} km/L")
        print(f" - Recommendation: '{res1['recommendation']}'")
        
        assert res1["total_trips"] == 0
        assert res1["utilization"] == 0
        assert res1["recommendation"] == "Vehicle underutilized."

        # Test Case 2: High Utilization / Normal operating (42 trips, 81% utilization)
        print("\n[Test 2] Testing vehicle with high utilization (total_trips = 42, utilization = 81%)...")
        res2 = service.generate_report(db, str(v_high))
        print("Test 2 Result:")
        print(f" - Vehicle Number: {res2['vehicle']}")
        print(f" - Trips: {res2['total_trips']}")
        print(f" - Avg distance: {res2['average_distance']} km (Expected: 328.4)")
        print(f" - Fuel efficiency: {res2['fuel_efficiency']} km/L (Expected: 7.5)")
        print(f" - Utilization: {res2['utilization']}% (Expected: 81)")
        print(f" - Recommendation: '{res2['recommendation']}'")
        
        assert res2["vehicle"] == v_high_num
        assert res2["total_trips"] == 42
        assert abs(res2["average_distance"] - 328.4) <= 1.0
        assert res2["fuel_efficiency"] == 7.5
        assert res2["utilization"] == 81
        assert res2["recommendation"] == "Vehicle operating normally."

        # Test Case 3: Poor fuel efficiency (3.5 km/L vs fleet avg)
        print("\n[Test 3] Testing vehicle with poor fuel efficiency...")
        res3 = service.generate_report(db, str(v_poor))
        print("Test 3 Result:")
        print(f" - Fuel efficiency: {res3['fuel_efficiency']} km/L")
        print(f" - Recommendation: '{res3['recommendation']}'")
        
        assert res3["fuel_efficiency"] == 3.5
        assert res3["recommendation"] == "Vehicle fuel efficiency is below fleet average."

        # Test Case 4: Frequent maintenance (maintenance logs = 6)
        print("\n[Test 4] Testing vehicle with frequent maintenance logs (> 5)...")
        res4 = service.generate_report(db, str(v_maint))
        print("Test 4 Result:")
        print(f" - Maintenance Count: {res4['maintenance_count']}")
        print(f" - Recommendation: '{res4['recommendation']}'")
        
        assert res4["maintenance_count"] == 6
        assert res4["recommendation"] == "Frequent maintenance detected."

        # Test Case 5: Vehicle Not Found
        print("\n[Test 5] Testing report generation with missing vehicle ID...")
        fake_uuid = str(uuid.uuid4())
        try:
            service.generate_report(db, fake_uuid)
            print("❌ Test 5 Failed: Non-existent vehicle ID did not raise exception.")
            assert False
        except VehicleUnavailableException:
            print("Test 5 Success! Correctly raised VehicleUnavailableException.")

        print("\nAll Fleet Analytics Agent tests executed successfully. Rolling back database changes.")
    except Exception as e:
        print(f"\n[ERROR] Test Execution Failed: {e}")
        db.rollback()
        raise e
    finally:
        db.rollback()
        db.close()

if __name__ == "__main__":
    run_tests()
