import os
import sys
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import text

# Traverse up 4 levels to reach the workspace root (AgentFleet/)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from backend.app.database.supabase import SessionLocal
from backend.app.agents.maintenance.service import MaintenanceService
from backend.app.shared.exceptions import VehicleUnavailableException

def create_mock_maintenance_data(db: Session):
    print("Setting up temporary mock vehicles for Maintenance Agent test...")
    
    unique_v1 = f"KA-MN-{uuid.uuid4().hex[:4].upper()}"
    unique_v2 = f"KA-MN-{uuid.uuid4().hex[:4].upper()}"
    unique_v3 = f"KA-MN-{uuid.uuid4().hex[:4].upper()}"
    
    # 1. Healthy Vehicle (Health Score = 86)
    v1_query = text("""
        INSERT INTO vehicles (vehicle_number, vehicle_type, capacity_kg, fuel_type, fuel_level, status, health_score)
        VALUES (:vehicle_number, 'Reefer Truck', 8000.0, 'Diesel', 80.0, 'Available', 86.0)
        RETURNING id
    """)
    v1_id = db.execute(v1_query, {"vehicle_number": unique_v1}).scalar()
    
    # 2. Service Recommended Vehicle (Health Score = 70)
    v2_query = text("""
        INSERT INTO vehicles (vehicle_number, vehicle_type, capacity_kg, fuel_type, fuel_level, status, health_score)
        VALUES (:vehicle_number, 'Dry Van', 5000.0, 'Gasoline', 95.0, 'Available', 70.0)
        RETURNING id
    """)
    v2_id = db.execute(v2_query, {"vehicle_number": unique_v2}).scalar()
    
    # 3. Critical Vehicle (Health Score = 41)
    v3_query = text("""
        INSERT INTO vehicles (vehicle_number, vehicle_type, capacity_kg, fuel_type, fuel_level, status, health_score)
        VALUES (:vehicle_number, 'Box Truck', 3500.0, 'Diesel', 40.0, 'Available', 41.0)
        RETURNING id
    """)
    v3_id = db.execute(v3_query, {"vehicle_number": unique_v3}).scalar()
    
    db.flush()
    return v1_id, v2_id, v3_id

def run_tests():
    db = SessionLocal()
    print("Starting integration test for Vehicle Health & Maintenance Agent...")
    try:
        # Initialize Mock Data
        v1_id, v2_id, v3_id = create_mock_maintenance_data(db)
        service = MaintenanceService()

        # Test Case A: Healthy Vehicle (health_score = 86)
        print("\n[Test 1] Testing healthy vehicle check (score = 86)...")
        res1 = service.evaluate_vehicle(db, str(v1_id))
        print("Test 1 Result Payload:")
        print(f" - ID: {res1['vehicle_id']}")
        print(f" - Status: {res1['vehicle_status']} (Expected: Healthy)")
        print(f" - Service after: {res1.get('next_service_after_km')} km (Expected: 1800)")
        print(f" - Message: '{res1['message']}'")
        
        assert res1["vehicle_status"] == "Healthy"
        assert res1["next_service_after_km"] == 1800
        assert res1["health_score"] == 86

        # Test Case B: Service Recommended (health_score = 70)
        print("\n[Test 2] Testing service recommended vehicle check (score = 70)...")
        res2 = service.evaluate_vehicle(db, str(v2_id))
        print("Test 2 Result Payload:")
        print(f" - Status: {res2['vehicle_status']} (Expected: Service Recommended)")
        print(f" - Service after: {res2.get('next_service_after_km')} km (Expected: 1000)")
        
        assert res2["vehicle_status"] == "Service Recommended"
        assert res2["next_service_after_km"] == 1000
        assert res2["health_score"] == 70

        # Test Case C: Maintenance Required (health_score = 41)
        print("\n[Test 3] Testing critical vehicle requiring immediate maintenance (score = 41)...")
        res3 = service.evaluate_vehicle(db, str(v3_id))
        print("Test 3 Result Payload:")
        print(f" - Status: {res3['vehicle_status']} (Expected: Maintenance Required)")
        print(f" - Message: '{res3['message']}'")
        
        assert res3["vehicle_status"] == "Maintenance Required"
        assert "next_service_after_km" not in res3
        assert res3["health_score"] == 41

        # Check DB State for Critical Vehicle: Vehicle Status in DB should be updated to 'Maintenance'
        v3_db_status = db.execute(
            text("SELECT status FROM vehicles WHERE id = :id"),
            {"id": v3_id}
        ).scalar()
        print(f"DB Check: Vehicle {v3_id} status in DB = '{v3_db_status}' (Expected: Maintenance)")
        assert v3_db_status == "Maintenance"

        # Check DB State for Critical Vehicle: Maintenance Log record must be inserted
        log_count = db.execute(
            text("SELECT COUNT(*) FROM maintenance_logs WHERE vehicle_id = :id"),
            {"id": v3_id}
        ).scalar()
        print(f"DB Check: Maintenance log entries inserted = {log_count} (Expected: 1)")
        assert log_count == 1

        # Test Case D: Vehicle Not Found
        print("\n[Test 4] Testing vehicle health lookup with non-existent ID...")
        fake_uuid = str(uuid.uuid4())
        try:
            service.evaluate_vehicle(db, fake_uuid)
            print("❌ Test 4 Failed: Non-existent vehicle ID did not raise exception.")
            assert False
        except VehicleUnavailableException:
            print("Test 4 Success! Correctly raised VehicleUnavailableException.")

        print("\nAll Maintenance Agent tests executed successfully. Rolling back database changes.")
    except Exception as e:
        print(f"\n[ERROR] Test Execution Failed: {e}")
        db.rollback()
        raise e
    finally:
        db.rollback()
        db.close()

if __name__ == "__main__":
    run_tests()
