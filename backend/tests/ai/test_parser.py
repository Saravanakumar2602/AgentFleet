import os
import sys

# Traverse up 4 levels to reach the workspace root (AgentFleet/)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from backend.app.ai.parser import IntentParser
from backend.app.ai.intent import FleetIntent

def test_intent_parser():
    print("Testing Natural Language Intent Parser rules classification...")

    # 1. Test Dispatch classification
    res_dispatch = IntentParser.parse("Please dispatch vehicle to main dock with cargo capacity of 4500 kg")
    assert res_dispatch["intent"] == FleetIntent.DISPATCH
    assert res_dispatch["parameters"]["weight"] == 4500.0

    # 2. Test Route classification
    res_route = IntentParser.parse("Generate routing path coordinates: 12.9715,77.5945 to 13.0827,80.2707")
    assert res_route["intent"] == FleetIntent.ROUTE
    assert len(res_route["parameters"]["coordinates"]) == 2
    assert res_route["parameters"]["coordinates"][0] == "12.9715,77.5945"

    # 3. Test Maintenance classification
    res_maint = IntentParser.parse("Check diagnostic health scores for vehicle 1a459f3c-9bdc-4bae-b55e-0ec1d2ac627f")
    assert res_maint["intent"] == FleetIntent.MAINTENANCE
    assert res_maint["parameters"]["target_id"] == "1a459f3c-9bdc-4bae-b55e-0ec1d2ac627f"

    # 4. Test Analytics classification
    res_analytics = IntentParser.parse("Output utilization statistics reports for all reefer trucks")
    assert res_analytics["intent"] == FleetIntent.ANALYTICS

    # 5. Test Customer classification
    res_cust = IntentParser.parse("Send a customer tracking alert notification")
    assert res_cust["intent"] == FleetIntent.CUSTOMER

    # 6. Test Workflow classification
    res_wf = IntentParser.parse("Initiate delivery workflow for route")
    assert res_wf["intent"] == FleetIntent.WORKFLOW

    # 7. Test Unknown
    res_unknown = IntentParser.parse("Sing me a happy song about fleet logistics")
    assert res_unknown["intent"] == FleetIntent.UNKNOWN

    print("IntentParser tests executed successfully!")

if __name__ == "__main__":
    test_intent_parser()
