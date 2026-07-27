import os
import sys
import uuid
import json
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from sqlalchemy import text

# Traverse up 4 levels to reach the workspace root (AgentFleet/)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from backend.app.database.supabase import SessionLocal
from backend.app.agents.supervisor.service import SupervisorService
from backend.app.shared.exceptions import AIParserException

def create_mock_supervisor_chat_data(db: Session):
    print("Setting up temporary mock vehicle, driver, and location details for Supervisor Chat test...")
    
    unique_email = f"supervisor_chat_{uuid.uuid4().hex[:6]}@agentfleet.com"
    unique_license = f"LIC-SVC-{uuid.uuid4().hex[:4].upper()}"
    unique_vehicle = f"KA-SVC-{uuid.uuid4().hex[:4].upper()}"
    
    # 1. Insert User
    user_query = text("""
        INSERT INTO users (name, email, password_hash, role)
        VALUES ('Supervisor Chat Driver', :email, 'hashedpassword', 'Driver')
        RETURNING id
    """)
    user_id = db.execute(user_query, {"email": unique_email}).scalar()
    
    # 2. Insert Driver
    driver_query = text("""
        INSERT INTO drivers (user_id, license_number, phone, experience_years, status, rating)
        VALUES (:user_id, :license, '+919999988881', 6, 'Available', 4.9)
        RETURNING id
    """)
    driver_id = db.execute(driver_query, {"user_id": user_id, "license": unique_license}).scalar()
    
    # 3. Insert Vehicle (capacity 8000 kg, health score 86)
    vehicle_query = text("""
        INSERT INTO vehicles (vehicle_number, vehicle_type, capacity_kg, fuel_type, fuel_level, status, health_score)
        VALUES (:vehicle_number, 'Reefer Truck', 8000.0, 'Diesel', 80.0, 'Available', 86.0)
        RETURNING id
    """)
    vehicle_id = db.execute(vehicle_query, {"vehicle_number": unique_vehicle}).scalar()
    
    # 4. Insert Location (Bangalore)
    db.execute(text("""
        INSERT INTO vehicle_locations (vehicle_id, latitude, longitude, speed)
        VALUES (:vehicle_id, 12.9715, 77.5945, 0.0)
    """), {"vehicle_id": vehicle_id})
    
    db.flush()
    return vehicle_id, driver_id, unique_vehicle

def run_tests():
    db = SessionLocal()
    print("Starting integration test for AI-Powered Supervisor Agent...")
    try:
        # Create mock records
        vehicle_id, driver_id, vehicle_num = create_mock_supervisor_chat_data(db)
        service = SupervisorService()

        # Mock the GroqAdapter instance in LLMFactory registry
        mock_groq = MagicMock()
        
        with patch("backend.app.ai.llm_factory.LLMFactory.get", return_value=mock_groq):
            
            # Test Case 1: Successful Workflow & Combined Response Format & Execution Timing
            print("\n[Test 1] Testing successful workflow execution via AI Supervisor chat...")
            mock_groq.chat.return_value = """
            {
              "intent": "WORKFLOW",
              "workflow": "fleet_delivery",
              "pickup": "Chennai",
              "destination": "Coimbatore",
              "weight": 2500,
              "priority": "Normal"
            }
            """
            
            res1 = service.chat_workflow(
                db=db,
                message="Deliver 2.5 tons from Chennai to Coimbatore tomorrow morning."
            )
            print("Test 1 Result:")
            print(f" - Status: {res1['status']}")
            print(f" - Workflow: {res1['workflow']}")
            print(f" - LLM Latency: {res1['llm_latency_ms']} ms")
            print(f" - Total Time: {res1['total_execution_time_ms']} ms")
            print(f" - Results keys: {res1['results'].keys()}")
            
            assert res1["status"] == "success"
            assert res1["workflow"] == "fleet_delivery"
            assert isinstance(res1["llm_latency_ms"], int)
            assert isinstance(res1["total_execution_time_ms"], int)
            
            # Verify results keys
            results = res1["results"]
            assert results["dispatch"]["trip_id"] is not None
            assert results["route"]["distance_km"] == 427.4
            assert results["route"]["estimated_duration"] == "6h 58m"
            assert results["maintenance"]["health_score"] == 86
            assert results["maintenance"]["vehicle_status"] == "Healthy"
            assert isinstance(results["analytics"]["utilization"], int) and 0 <= results["analytics"]["utilization"] <= 100
            assert "Your shipment has been dispatched" in results["customer"]["customer_message"]

            # Test Case 2: Dispatch Failure Propagation
            print("\n[Test 2] Testing workflow failure propagation via AI Supervisor chat...")
            mock_groq.chat.return_value = """
            {
              "intent": "WORKFLOW",
              "workflow": "fleet_delivery",
              "pickup": "Chennai",
              "destination": "Coimbatore",
              "weight": 99999.0,
              "priority": "High"
            }
            """
            
            res2 = service.chat_workflow(
                db=db,
                message="Deliver 100 tons from Chennai to Coimbatore now."
            )
            print("Test 2 Result:")
            print(f" - Status: {res2['status']}")
            print(f" - Failed Agent: {res2.get('failed_agent')}")
            print(f" - Reason: {res2.get('reason')}")
            
            assert res2["status"] == "failed"
            assert res2["failed_agent"] == "Dispatch"
            assert "No suitable vehicle" in res2["reason"]

            # Test Case 3: Invalid JSON Recovery / Failure
            print("\n[Test 3] Testing AI Supervisor chat recovery with invalid JSON outputs...")
            # Simulate double invalid JSON failure raising AIParserException
            mock_groq.chat.side_effect = AIParserException("Invalid JSON from LLM")
            
            try:
                service.chat_workflow(
                    db=db,
                    message="Please sing me a happy song about fleet logistics."
                )
                print("❌ Test 3 Failed: Invalid JSON output did not raise AIParserException.")
                assert False
            except AIParserException as e:
                print("Test 3 Success! Correctly raised AIParserException on LLM JSON failures.")
                assert "Invalid JSON" in e.message

        print("\nAll AI Supervisor Agent tests executed successfully. Rolling back database changes.")
    except Exception as e:
        print(f"\n[ERROR] Test Execution Failed: {e}")
        db.rollback()
        raise e
    finally:
        db.rollback()
        db.close()

if __name__ == "__main__":
    run_tests()
