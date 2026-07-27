import os
import sys
import json
from unittest.mock import patch, MagicMock

# Traverse up 4 levels to reach the workspace root (AgentFleet/)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from backend.app.ai.adapters.groq_adapter import GroqAdapter
from backend.app.shared.exceptions import AIParserException

def test_groq_health_check():
    print("\n[Test 1] Testing Groq health check connectivity mapping...")
    
    # When api_key is mock/missing, should return False
    adapter = GroqAdapter(api_key="mock-key")
    assert adapter.health_check() is False

    # Mock successful models list call
    with patch.object(adapter.client.models, "list") as mock_list:
        adapter.api_key = "valid-api-key"
        mock_list.return_value = MagicMock()
        assert adapter.health_check() is True

        # Mock exception
        mock_list.side_effect = Exception("Connection Timeout")
        assert adapter.health_check() is False

def test_groq_simple_prompt():
    print("\n[Test 2] Testing simple prompt generation (non-JSON)...")
    adapter = GroqAdapter(api_key="valid-api-key")

    mock_choice = MagicMock()
    mock_choice.message.content = "This is a simple response."
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    with patch.object(adapter.client.chat.completions, "create", return_value=mock_response) as mock_create:
        res = adapter.generate("Hello simple assistant")
        assert res == "This is a simple response."
        mock_create.assert_called_once()

def test_groq_json_validation_and_retry():
    print("\n[Test 3] Testing JSON validation and retry sequences...")
    adapter = GroqAdapter(api_key="valid-api-key")

    # Scenario A: First call fails JSON check, second call succeeds
    mock_choice_1 = MagicMock()
    mock_choice_1.message.content = "Sorry, this is plain text not JSON."
    mock_choice_2 = MagicMock()
    mock_choice_2.message.content = '{"intent": "WORKFLOW", "workflow": "fleet_delivery"}'
    
    mock_res_1 = MagicMock(choices=[mock_choice_1])
    mock_res_2 = MagicMock(choices=[mock_choice_2])

    with patch.object(adapter.client.chat.completions, "create", side_effect=[mock_res_1, mock_res_2]) as mock_create:
        # Prompt contains word 'JSON' to trigger JSON validation path
        res = adapter.generate("Extract details to JSON format: Chennai to Bangalore 2500 kg")
        assert res == '{"intent": "WORKFLOW", "workflow": "fleet_delivery"}'
        assert mock_create.call_count == 2
        print("Success: Retry logic caught invalid JSON and recovered on second attempt.")

    # Scenario B: Both calls fail JSON check, raises AIParserException
    mock_choice_fail = MagicMock()
    mock_choice_fail.message.content = "Still not JSON format."
    mock_res_fail = MagicMock(choices=[mock_choice_fail])

    with patch.object(adapter.client.chat.completions, "create", return_value=mock_res_fail) as mock_create_fail:
        try:
            adapter.generate("Extract details to JSON: weight = 1500")
            print("❌ Scenario B Failed: Did not raise AIParserException on double JSON failures.")
            assert False
        except AIParserException as e:
            print("Success: Correctly raised AIParserException on continuous JSON validation failures.")
            assert "Failed to generate valid JSON" in e.message
            assert mock_create_fail.call_count == 2

def test_groq_intent_extraction():
    print("\n[Test 4] Testing intent extraction structured payload responses...")
    adapter = GroqAdapter(api_key="valid-api-key")

    mock_choice = MagicMock()
    mock_choice.message.content = """
    ```json
    {
      "intent": "WORKFLOW",
      "workflow": "fleet_delivery",
      "pickup": "Chennai",
      "destination": "Bangalore",
      "weight": 2500,
      "priority": "Normal"
    }
    ```
    """
    mock_res = MagicMock(choices=[mock_choice])

    with patch.object(adapter.client.chat.completions, "create", return_value=mock_res) as mock_create:
        res = adapter.generate("Deliver 2.5 tons from Chennai to Bangalore JSON")
        parsed = json.loads(res)
        
        assert parsed["intent"] == "WORKFLOW"
        assert parsed["workflow"] == "fleet_delivery"
        assert parsed["pickup"] == "Chennai"
        assert parsed["destination"] == "Bangalore"
        assert parsed["weight"] == 2500
        assert parsed["priority"] == "Normal"
        print("Success: Correctly stripped markdown JSON syntax and parsed parameters.")

def run_all_tests():
    print("Starting Groq Adapter unit tests...")
    test_groq_health_check()
    test_groq_simple_prompt()
    test_groq_json_validation_and_retry()
    test_groq_intent_extraction()
    print("\nAll Groq Adapter tests completed successfully!")

if __name__ == "__main__":
    run_all_tests()
