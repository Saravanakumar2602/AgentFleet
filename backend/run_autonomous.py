import os
import sys
import json
from sqlalchemy import text

# Add parent directory to sys.path to allow absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.database.supabase import SessionLocal
from backend.app.registry.registry import get_agent

def reset_database_state(db):
    """
    Resets the database state for vehicles, drivers, and trips
    to allow fresh runs of the autonomous workflow simulation.
    """
    print("--- [Reset] Clearing Database State for Testing ---")
    try:
        # Delete all trips
        db.execute(text("DELETE FROM trips"))
        # Reset vehicles to 'Available'
        db.execute(text("UPDATE vehicles SET status = 'Available'"))
        # Reset drivers to 'Available'
        db.execute(text("UPDATE drivers SET status = 'Available'"))
        db.commit()
        print(">> Database reset successful: Trips cleared. All vehicles and drivers set to 'Available'.\n")
    except Exception as e:
        db.rollback()
        print(f">> Failed to reset database: {e}\n")

def execute_autonomous_delivery(pickup: str, destination: str, cargo_weight: float, reset_first: bool = False):
    """
    Executes the multi-agent fleet delivery workflow programmatically step-by-step.
    Prints the output of each agent immediately after its execution.
    """
    db = SessionLocal()

    if reset_first:
        reset_database_state(db)

    print(f"==========================================")
    print(f"--- Starting Autonomous Multi-Agent Run ---")
    print(f"Pickup Coordinates: {pickup}")
    print(f"Destination Coordinates: {destination}")
    print(f"Cargo Weight: {cargo_weight} kg")
    print(f"==========================================\n")

    checkpoint_data = {}
    
    try:
        # Step 1: Dispatch Agent
        print("[Step 1/5] Executing Dispatch Agent...")
        dispatch_agent = get_agent("dispatch")
        if not dispatch_agent:
            raise RuntimeError("Dispatch Agent not found in registry.")
        
        dispatch_res = dispatch_agent.run(
            db=db,
            task_data={
                "pickup": pickup,
                "destination": destination,
                "weight": float(cargo_weight)
            }
        )
        print(">> Dispatch Agent Output:")
        print(json.dumps(dispatch_res, indent=2))
        print("-" * 50)
        
        checkpoint_data["trip_id"] = dispatch_res["trip_id"]
        checkpoint_data["vehicle_id"] = dispatch_res["vehicle"]["id"]
        checkpoint_data["driver_id"] = dispatch_res["driver"]["id"]

        # Step 2: Route Agent
        print("[Step 2/5] Executing Route Agent...")
        route_agent = get_agent("route")
        if not route_agent:
            raise RuntimeError("Route Agent not found in registry.")
            
        route_res = route_agent.run(
            db=db,
            task_data={
                "vehicle_id": checkpoint_data["vehicle_id"],
                "pickup": pickup,
                "destination": destination
            }
        )
        print(">> Route Agent Output:")
        print(json.dumps(route_res, indent=2))
        print("-" * 50)

        # Create a placeholder analytics record so the Analytics Agent has real records to calculate efficiency
        try:
            duration_str = route_res.get("estimated_duration", "0")
            minutes_val = 0
            if "h" in duration_str:
                parts = duration_str.split("h")
                hours_part = parts[0].strip()
                mins_part = parts[1].replace("m", "").strip() if len(parts) > 1 else "0"
                try:
                    minutes_val = int(hours_part) * 60 + int(mins_part or 0)
                except:
                    minutes_val = 240
            else:
                try:
                    minutes_val = int(duration_str.replace("m", "").strip())
                except:
                    minutes_val = 240
            
            db.execute(text("""
                INSERT INTO analytics (trip_id, fuel_used, average_speed, cost, delivery_time, created_at)
                VALUES (:trip_id, :fuel_used, :average_speed, :cost, :delivery_time, now())
            """), {
                "trip_id": checkpoint_data["trip_id"],
                "fuel_used": route_res["estimated_fuel"],
                "average_speed": 61.26,
                "cost": round(route_res["estimated_fuel"] * 1.15, 2),
                "delivery_time": minutes_val
            })
            db.commit()
        except Exception as analytics_err:
            print(f"Warning: Failed to create placeholder analytics record: {analytics_err}")
            db.rollback()

        # Step 3: Maintenance Agent
        print("[Step 3/5] Executing Maintenance Agent...")
        maint_agent = get_agent("maintenance")
        if not maint_agent:
            raise RuntimeError("Maintenance Agent not found in registry.")
            
        maint_res = maint_agent.run(
            db=db,
            task_data={
                "vehicle_id": checkpoint_data["vehicle_id"]
            }
        )
        print(">> Maintenance Agent Output:")
        print(json.dumps(maint_res, indent=2))
        print("-" * 50)

        # Step 4: Analytics Agent
        print("[Step 4/5] Executing Analytics Agent...")
        analytics_agent = get_agent("analytics")
        if not analytics_agent:
            raise RuntimeError("Analytics Agent not found in registry.")
            
        analytics_res = analytics_agent.run(
            db=db,
            task_data={
                "vehicle_id": checkpoint_data["vehicle_id"]
            }
        )
        print(">> Analytics Agent Output:")
        print(json.dumps(analytics_res, indent=2))
        print("-" * 50)

        # Step 5: Customer Agent
        print("[Step 5/5] Executing Customer Agent...")
        customer_agent = get_agent("customer")
        if not customer_agent:
            raise RuntimeError("Customer Agent not found in registry.")
            
        customer_res = customer_agent.run(
            db=db,
            task_data={
                "trip_id": checkpoint_data["trip_id"]
            }
        )
        print(">> Customer Agent Output:")
        print(json.dumps(customer_res, indent=2))
        print("=" * 50)

        print("\n--- All Agents Executed Successfully autonomously! ---")

    except Exception as e:
        print(f"\n[ERROR] Execution halted: {e}")
        print("\n[TIP] If execution failed due to unavailable drivers/vehicles, run:")
        print("      .\\.venv\\Scripts\\python.exe .\\backend\\run_autonomous.py --reset")
        
        # Rollback logic to reset database state on failure
        trip_id = checkpoint_data.get("trip_id")
        vehicle_id = checkpoint_data.get("vehicle_id")
        driver_id = checkpoint_data.get("driver_id")
        
        if trip_id or vehicle_id or driver_id:
            print("\nTriggering database rollback to clean up state...")
            try:
                if trip_id:
                    db.execute(text("DELETE FROM notifications WHERE trip_id = :trip_id"), {"trip_id": trip_id})
                    db.execute(text("DELETE FROM trips WHERE id = :id"), {"id": trip_id})
                if vehicle_id:
                    db.execute(text("UPDATE vehicles SET status = 'Available' WHERE id = :id"), {"id": vehicle_id})
                if driver_id:
                    db.execute(text("UPDATE drivers SET status = 'Available' WHERE id = :id"), {"id": driver_id})
                db.commit()
                print("Rollback completed successfully.")
            except Exception as rollback_err:
                db.rollback()
                print(f"Rollback failed: {rollback_err}")
    finally:
        db.close()

if __name__ == "__main__":
    # Check if user passed --reset flag
    reset_flag = "--reset" in sys.argv

    # Test coordinates: Chennai (13.0827,80.2707) to Bangalore (12.9715,77.5945)
    execute_autonomous_delivery(
        pickup="13.0827,80.2707",
        destination="12.9715,77.5945",
        cargo_weight=3500.0,
        reset_first=reset_flag
    )
