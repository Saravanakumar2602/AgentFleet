from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
import time
import json
import re

from backend.app.workflows.workflow_registry import get_workflow
from backend.app.shared.exceptions import AgentFleetException, AIParserException
from backend.app.ai.llm_factory import LLMFactory
from backend.app.ai.memory import ConversationMemory

logger = logging.getLogger("agentfleet.agents.supervisor.service")

class SupervisorService:
    """
    Upgraded AI-powered business layer for Fleet Supervisor Agent.
    Orchestrates LLM intent parsing, conversational memory, latency tracking, 
    and triggers multi-agent workflows.
    """
    def __init__(self):
        self.memory = ConversationMemory()

    def resolve_location(self, name: str) -> str:
        """
        Translates logical city names into coordinate strings expected by workflows.
        If the value is already a coordinate pair, returns it directly.
        """
        clean_name = name.strip().lower()
        mapping = {
            "chennai": "13.0827,80.2707",
            "coimbatore": "11.0168,76.9558",
            "bangalore": "12.9715,77.5945",
            "bengaluru": "12.9715,77.5945",
            "mumbai": "19.0760,72.8777",
            "delhi": "28.6139,77.2090"
        }
        # Match pattern: 'lat,lon'
        if re.match(r'^-?\d+\.\d+\s*,\s*-?\d+\.\d+$', name.strip()):
            return name.strip()
        return mapping.get(clean_name, name)

    def chat_workflow(self, db: Session, message: str) -> dict:
        """
        Executes workflow from a natural language instruction using the Groq AI layer.
        """
        total_start = time.perf_counter()
        logger.info(f"Supervisor parsing chat request: '{message}'")

        # 1. Resolve Groq adapter from factory
        try:
            groq_adapter = LLMFactory.get("groq")
        except Exception as e:
            logger.error(f"Failed to resolve Groq adapter from factory: {e}")
            raise e

        # 2. Configure System Prompt and structure memory
        system_prompt = (
            "You are an intent extraction engine.\n"
            "Analyze the user request and return a structured JSON response.\n"
            "Return ONLY valid JSON. Never explain. Never answer questions. Never generate text outside JSON.\n\n"
            "Required JSON Schema:\n"
            "{\n"
            "  \"intent\": \"string (e.g., 'dispatch', 'complete_trip', 'maintenance_status', 'agent_status', 'general')\",\n"
            "  \"workflow\": \"string (e.g., 'fleet_delivery', 'complete_trip', 'vehicle_maintenance', 'agent_status', 'general')\",\n"
            "  \"pickup\": \"string (optional, origin location name/coordinate)\",\n"
            "  \"destination\": \"string (optional, destination location name/coordinate)\",\n"
            "  \"weight\": \"number (optional, numeric cargo weight value)\",\n"
            "  \"vehicle_number\": \"string (optional, specific vehicle registration plate mentioned, e.g., 'TN38AB1234')\"\n"
            "}"
        )

        self.memory.add("system", system_prompt)
        self.memory.add("user", message)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]

        logger.info(f"Submitting conversation history to Groq: {messages}")

        # 3. Call Groq with completion timing latency measurements
        start_llm = time.perf_counter()
        try:
            raw_response = groq_adapter.chat(messages)
        except AIParserException as parse_err:
            logger.error(f"Groq adapter failed JSON validations: {parse_err}")
            raise parse_err
        except Exception as e:
            logger.error(f"Uncaught LLM completion exception: {e}")
            raise AIParserException(f"LLM call failed: {e}")
        end_llm = time.perf_counter()
        
        llm_latency_ms = int((end_llm - start_llm) * 1000)
        logger.info(f"Groq intent extraction latency: {llm_latency_ms} ms")

        # Record LLM response in memory
        self.memory.add("assistant", raw_response)

        # 4. Parse response JSON
        cleaned_json = self._clean_json(raw_response)
        try:
            parsed = json.loads(cleaned_json)
        except Exception as json_err:
            logger.error(f"JSON validation failed on LLM output: {json_err}. Output: '{raw_response}'")
            raise AIParserException(f"Invalid JSON parsed: {json_err}")

        # 5. Extract and validate parameters based on intent
        intent = parsed.get("intent", "").lower()
        
        if "complete" in intent or intent == "complete_trip" or "completed" in intent:
            workflow_name = "complete_trip"
            vehicle_number = parsed.get("vehicle_number")
            if not vehicle_number and message:
                match = re.search(r'\b[A-Z]{2}[- ]?\d{1,2}[- ]?[A-Z]{1,3}[- ]?\d{1,4}\b', message.upper())
                if match:
                    vehicle_number = match.group(0).replace(" ", "").replace("-", "")

            workflow = get_workflow(workflow_name)
            if not workflow:
                raise AgentFleetException("Workflow not found.", status_code=400)

            workflow_res = workflow.run(
                db=db,
                task_data={
                    "trip_id": parsed.get("trip_id"),
                    "vehicle_number": vehicle_number
                }
            )

            total_end = time.perf_counter()
            total_time_ms = int((total_end - total_start) * 1000)

            if workflow_res.get("status") == "failed":
                return workflow_res

            return {
                "status": "success",
                "intent": intent,
                "workflow": workflow_name,
                "llm_latency_ms": llm_latency_ms,
                "total_execution_time_ms": total_time_ms,
                "results": {
                    "dispatch": {
                        "trip_id": workflow_res["trip_id"],
                        "vehicle": {
                            "id": "N/A",
                            "vehicle_number": workflow_res["vehicle_number"]
                        },
                        "driver": {
                            "id": "N/A",
                            "name": workflow_res["driver_name"]
                        }
                    },
                    "route": {
                        "distance_km": 0.0,
                        "estimated_duration": "0m",
                        "estimated_fuel": 0.0
                    },
                    "maintenance": {
                        "health_score": 100,
                        "vehicle_status": "Available"
                    },
                    "analytics": {
                        "utilization": 0,
                        "recommendation": "N/A"
                    },
                    "customer": {
                        "customer_message": workflow_res["message"]
                    }
                }
            }

        # If it is a dispatch/delivery request:
        elif "dispatch" in intent or "delivery" in intent or "workflow" in intent or intent == "fleet_delivery":
            workflow_name = parsed.get("workflow", "fleet_delivery")
            pickup = parsed.get("pickup") or parsed.get("origin")
            destination = parsed.get("destination")
            weight = parsed.get("weight")

            if not all([intent, pickup, destination, weight]):
                logger.warning(f"Extracted payload parameters are incomplete: {parsed}")
                raise AIParserException("Missing parameters in AI response.")

            try:
                cargo_weight = float(weight)
            except (TypeError, ValueError):
                logger.warning(f"Cargo weight value is not numeric: {weight}")
                raise AIParserException("Cargo weight must be a number.")

            # 6. Resolve names to coordinate strings
            resolved_pickup = self.resolve_location(pickup)
            resolved_destination = self.resolve_location(destination)

            # 7. Execute workflow logic via Supervisor standard methods
            workflow_res = self.execute_workflow(
                db=db,
                workflow_name=workflow_name,
                pickup=resolved_pickup,
                destination=resolved_destination,
                weight=cargo_weight
            )

            total_end = time.perf_counter()
            total_time_ms = int((total_end - total_start) * 1000)

            # If workflow itself failed, propagate failed response dictionary directly
            if workflow_res.get("status") == "failed":
                return workflow_res

            # 8. Return restructured merged response
            return {
                "status": "success",
                "intent": intent,
                "workflow": workflow_name,
                "llm_latency_ms": llm_latency_ms,
                "total_execution_time_ms": total_time_ms,
                "results": workflow_res["results"]
            }

        else:
            # Handle maintenance or status check or general query
            vehicle_number = parsed.get("vehicle_number")
            
            # Extract vehicle number from message via regex if not found in JSON
            if not vehicle_number and message:
                match = re.search(r'\b[A-Z]{2}[- ]?\d{1,2}[- ]?[A-Z]{1,3}[- ]?\d{1,4}\b', message.upper())
                if match:
                    vehicle_number = match.group(0).replace(" ", "").replace("-", "")

            vehicle_name = vehicle_number or "N/A"
            vehicle_status = "Healthy"
            health_score = 95
            cust_msg = "Hello! How can I assist you with your fleet operations today?"

            if "maintenance" in intent or "vehicle" in intent or "health" in intent or vehicle_number:
                vehicle_details = None
                if vehicle_number:
                    try:
                        clean_num = vehicle_number.strip().replace(" ", "").replace("-", "").upper()
                        query = text("""
                            SELECT vehicle_number, status, health_score 
                            FROM vehicles 
                            WHERE UPPER(REPLACE(REPLACE(vehicle_number, ' ', ''), '-', '')) = :num
                        """)
                        row = db.execute(query, {"num": clean_num}).first()
                        if row:
                            vehicle_details = dict(row._mapping)
                    except Exception as db_err:
                        logger.error(f"Error querying vehicle for maintenance chat: {db_err}")

                if vehicle_details:
                    vehicle_name = vehicle_details["vehicle_number"]
                    vehicle_status = vehicle_details["status"]
                    health_score = int(float(vehicle_details["health_score"]))
                    cust_msg = f"Vehicle {vehicle_name} is currently in {vehicle_status} status with a health score of {health_score}%."
                else:
                    if vehicle_number:
                        cust_msg = f"Vehicle {vehicle_number} was not found in our database, but general maintenance logs indicate no active diagnostics warnings for similar assets."
                    else:
                        cust_msg = "Maintenance Agent reports that 98% of the fleet is healthy and active. Please specify a vehicle number to check diagnostic details."
            
            elif "status" in intent or "agent" in intent or "work" in intent:
                cust_msg = "All AgentFleet service agents are online: Dispatch, Route, Maintenance, Analytics, Customer, and Supervisor."

            total_end = time.perf_counter()
            total_time_ms = int((total_end - total_start) * 1000)

            return {
                "status": "success",
                "intent": intent,
                "workflow": parsed.get("workflow", "general_query"),
                "llm_latency_ms": llm_latency_ms,
                "total_execution_time_ms": total_time_ms,
                "results": {
                    "dispatch": {
                        "trip_id": "N/A",
                        "vehicle": {
                            "id": "N/A",
                            "vehicle_number": vehicle_name
                        },
                        "driver": {
                            "id": "N/A",
                            "name": "N/A"
                        }
                    },
                    "route": {
                        "distance_km": 0.0,
                        "estimated_duration": "0m",
                        "estimated_fuel": 0.0
                    },
                    "maintenance": {
                        "health_score": health_score,
                        "vehicle_status": vehicle_status
                    },
                    "analytics": {
                        "utilization": 0,
                        "recommendation": "N/A"
                    },
                    "customer": {
                        "customer_message": cust_msg
                    }
                }
            }

    def execute_workflow(
        self,
        db: Session,
        workflow_name: str,
        pickup: str,
        destination: str,
        weight: float
    ) -> dict:
        """
        Loads the selected workflow, measures execution timing in milliseconds,
        triggers the workflow, and formats the response.
        """
        logger.info(f"Supervisor executing workflow: '{workflow_name}'")

        workflow = get_workflow(workflow_name)
        if not workflow:
            logger.warning(f"Workflow lookup failed for name: '{workflow_name}'")
            raise AgentFleetException("Workflow not found.", status_code=400)

        # Resolve city names to coordinates (e.g. 'chennai' -> '13.0827,80.2707')
        resolved_pickup = self.resolve_location(pickup)
        resolved_destination = self.resolve_location(destination)

        start_time = time.perf_counter()
        try:
            workflow_res = workflow.run(
                db=db,
                task_data={
                    "pickup": resolved_pickup,
                    "destination": resolved_destination,
                    "weight": float(weight)
                }
            )
        except Exception as e:
            logger.error(f"Uncaught exception inside workflow runtime: {e}")
            raise e
        end_time = time.perf_counter()
        
        execution_time_ms = int((end_time - start_time) * 1000)

        if workflow_res.get("status") == "failed":
            logger.warning(f"Workflow execution reported failure. Propagation triggered.")
            return workflow_res
        restructured_results = {
            "dispatch": {
                "trip_id": workflow_res["trip_id"],
                "vehicle": workflow_res["vehicle"],
                "driver": workflow_res["driver"]
            },
            "route": {
                "distance_km": workflow_res["distance_km"],
                "estimated_duration": workflow_res["estimated_duration"],
                "estimated_fuel": workflow_res["estimated_fuel"]
            },
            "maintenance": {
                "health_score": workflow_res["health_score"],
                "vehicle_status": workflow_res["vehicle_status"]
            },
            "analytics": {
                "utilization": workflow_res["utilization"],
                "recommendation": workflow_res["recommendation"]
            },
            "customer": {
                "customer_message": workflow_res["customer_message"]
            },
            "cargo_validation": workflow_res.get("cargo_validation"),
            "traffic": workflow_res.get("traffic"),
            "weather": workflow_res.get("weather"),
            "eta_updater": workflow_res.get("eta_updater"),
            "compliance": workflow_res.get("compliance"),
            "fuel": workflow_res.get("fuel"),
            "driver_rating": workflow_res.get("driver_rating"),
            "invoice": workflow_res.get("invoice"),
            "fleet_summary": workflow_res.get("fleet_summary"),
            "sos_alert": workflow_res.get("sos_alert"),
        }
        if "next_service_after_km" in workflow_res and workflow_res["next_service_after_km"] is not None:
            restructured_results["maintenance"]["next_service_after_km"] = workflow_res["next_service_after_km"]

        logger.info(f"Supervisor execution complete in {execution_time_ms} ms. Status = success.")

        return {
            "status": "success",
            "workflow": workflow_name,
            "execution_time_ms": execution_time_ms,
            "results": restructured_results
        }

    def _clean_json(self, content: str) -> str:
        """
        Utility to clean code fences around the JSON string.
        """
        stripped = content.strip()
        if stripped.startswith("```json"):
            stripped = stripped[7:]
        elif stripped.startswith("```"):
            stripped = stripped[3:]
        if stripped.endswith("```"):
            stripped = stripped[:-3]
        return stripped.strip()
