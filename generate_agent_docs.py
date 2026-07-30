"""
generate_agent_docs.py
Generates a professional PDF document for each AgentFleet agent.
Output: backend/app/agents/<agent>/docs/<agent>_agent.pdf
Requires: reportlab  (pip install reportlab)
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# ─── Colour palette ────────────────────────────────────────────────────────────
BRAND_DARK   = colors.HexColor("#0f172a")
BRAND_BLUE   = colors.HexColor("#4f8ef7")
BRAND_VIOLET = colors.HexColor("#7c6af7")
BRAND_GREEN  = colors.HexColor("#10b981")
BRAND_AMBER  = colors.HexColor("#f59e0b")
BRAND_RED    = colors.HexColor("#f87171")
GREY_LIGHT   = colors.HexColor("#f1f5f9")
GREY_MID     = colors.HexColor("#94a3b8")
GREY_BORDER  = colors.HexColor("#e2e8f0")
WHITE        = colors.white
TEXT_MAIN    = colors.HexColor("#1e293b")
TEXT_SUB     = colors.HexColor("#475569")
CODE_BG      = colors.HexColor("#1e293b")
CODE_FG      = colors.HexColor("#7dd3fc")

# ─── Style helpers ──────────────────────────────────────────────────────────────
def make_styles():
    base = getSampleStyleSheet()
    S = {}
    S["cover_title"] = ParagraphStyle("cover_title",
        fontName="Helvetica-Bold", fontSize=28, textColor=WHITE,
        leading=34, spaceAfter=8, alignment=TA_CENTER)
    S["cover_sub"] = ParagraphStyle("cover_sub",
        fontName="Helvetica", fontSize=13, textColor=colors.HexColor("#94a3b8"),
        leading=18, spaceAfter=4, alignment=TA_CENTER)
    S["cover_badge"] = ParagraphStyle("cover_badge",
        fontName="Helvetica-Bold", fontSize=10, textColor=BRAND_BLUE,
        leading=14, spaceAfter=2, alignment=TA_CENTER)
    S["section"] = ParagraphStyle("section",
        fontName="Helvetica-Bold", fontSize=14, textColor=BRAND_BLUE,
        leading=18, spaceBefore=18, spaceAfter=6)
    S["subsection"] = ParagraphStyle("subsection",
        fontName="Helvetica-Bold", fontSize=11, textColor=TEXT_MAIN,
        leading=14, spaceBefore=10, spaceAfter=4)
    S["body"] = ParagraphStyle("body",
        fontName="Helvetica", fontSize=10, textColor=TEXT_MAIN,
        leading=15, spaceAfter=4)
    S["body_sub"] = ParagraphStyle("body_sub",
        fontName="Helvetica", fontSize=9.5, textColor=TEXT_SUB,
        leading=14, spaceAfter=3)
    S["bullet"] = ParagraphStyle("bullet",
        fontName="Helvetica", fontSize=10, textColor=TEXT_MAIN,
        leading=15, leftIndent=14, spaceAfter=3,
        bulletIndent=4, bulletFontName="Helvetica-Bold")
    S["code"] = ParagraphStyle("code",
        fontName="Courier", fontSize=8.5, textColor=CODE_FG,
        leading=13, spaceAfter=2, leftIndent=0)
    S["footer"] = ParagraphStyle("footer",
        fontName="Helvetica", fontSize=8, textColor=GREY_MID,
        leading=11, alignment=TA_CENTER)
    return S

# ─── Building blocks ────────────────────────────────────────────────────────────
def cover_block(S, agent_name: str, role: str, color, description: str, api_path: str, pipeline_pos: str):
    """Dark gradient-style cover header."""
    # Use a table with coloured background to simulate a cover card
    cover_data = [[
        Paragraph(f"AgentFleet  ·  Agent Documentation", S["cover_badge"]),
    ]]
    t = Table(cover_data, colWidths=[17*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BRAND_DARK),
        ("TOPPADDING",    (0,0), (-1,-1), 28),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("RIGHTPADDING",  (0,0), (-1,-1), 10),
        ("ROUNDEDCORNERS", [8]),
    ]))

    title_data = [[Paragraph(agent_name, S["cover_title"])]]
    title_t = Table(title_data, colWidths=[17*cm])
    title_t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), BRAND_DARK),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("RIGHTPADDING",  (0,0), (-1,-1), 10),
    ]))

    role_data = [[Paragraph(f"Role: {role}  ·  Pipeline Position: {pipeline_pos}  ·  Endpoint: {api_path}", S["cover_sub"])]]
    role_t = Table(role_data, colWidths=[17*cm])
    role_t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), BRAND_DARK),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 20),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("RIGHTPADDING",  (0,0), (-1,-1), 10),
    ]))

    desc_data = [[Paragraph(description, ParagraphStyle("cd",
        fontName="Helvetica", fontSize=10.5, textColor=colors.HexColor("#cbd5e1"),
        leading=16, alignment=TA_CENTER))]]
    desc_t = Table(desc_data, colWidths=[17*cm])
    desc_t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), colors.HexColor("#1e293b")),
        ("TOPPADDING",    (0,0), (-1,-1), 12),
        ("BOTTOMPADDING", (0,0), (-1,-1), 18),
        ("LEFTPADDING",   (0,0), (-1,-1), 20),
        ("RIGHTPADDING",  (0,0), (-1,-1), 20),
        ("ROUNDEDCORNERS", [8]),
    ]))
    return [t, title_t, role_t, desc_t, Spacer(1, 0.5*cm)]


def section_header(S, title: str):
    return [
        HRFlowable(width="100%", thickness=1, color=BRAND_BLUE, spaceAfter=4),
        Paragraph(title, S["section"]),
    ]


def bullet_list(S, items):
    return [Paragraph(f"• &nbsp; {item}", S["bullet"]) for item in items]


def info_table(S, headers, rows, col_widths=None):
    """Styled table for API / error / module tables."""
    if col_widths is None:
        col_widths = [17*cm / len(headers)] * len(headers)
    data = [headers] + rows
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        # Header row
        ("BACKGROUND",   (0, 0), (-1, 0), BRAND_DARK),
        ("TEXTCOLOR",    (0, 0), (-1, 0), BRAND_BLUE),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, 0), 9.5),
        ("TOPPADDING",   (0, 0), (-1, 0), 7),
        ("BOTTOMPADDING",(0, 0), (-1, 0), 7),
        ("LEFTPADDING",  (0, 0), (-1,-1), 8),
        ("RIGHTPADDING", (0, 0), (-1,-1), 8),
        # Data rows
        ("FONTNAME",     (0, 1), (-1,-1), "Helvetica"),
        ("FONTSIZE",     (0, 1), (-1,-1), 9),
        ("TOPPADDING",   (0, 1), (-1,-1), 5),
        ("BOTTOMPADDING",(0, 1), (-1,-1), 5),
        ("TEXTCOLOR",    (0, 1), (-1,-1), TEXT_MAIN),
        ("ROWBACKGROUNDS",(0, 1), (-1,-1), [WHITE, GREY_LIGHT]),
        # Grid
        ("GRID",         (0, 0), (-1,-1), 0.4, GREY_BORDER),
        ("BOX",          (0, 0), (-1,-1), 0.8, GREY_BORDER),
        ("ROUNDEDCORNERS", [4]),
    ]))
    return [t, Spacer(1, 0.25*cm)]


def code_block(S, lines):
    """Dark background monospaced code block."""
    code_paras = [Paragraph(line.replace(" ", "&nbsp;").replace("<", "&lt;").replace(">", "&gt;"), S["code"])
                  for line in lines]
    t = Table([[p] for p in code_paras], colWidths=[17*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1,-1), CODE_BG),
        ("TOPPADDING",    (0, 0), (-1,-1), 3),
        ("BOTTOMPADDING", (0, 0), (-1,-1), 3),
        ("LEFTPADDING",   (0, 0), (-1,-1), 12),
        ("RIGHTPADDING",  (0, 0), (-1,-1), 12),
        ("ROUNDEDCORNERS", [6]),
    ]))
    return [Spacer(1, 0.15*cm), t, Spacer(1, 0.3*cm)]


# ═══════════════════════════════════════════════════════════════════════════════
# Agent document definitions
# ═══════════════════════════════════════════════════════════════════════════════

def build_dispatch(S):
    story = []
    story += cover_block(S,
        "Dispatch Agent", "Fleet Assigner", BRAND_BLUE,
        "Receives a cargo delivery request and allocates the best available vehicle and driver.",
        "POST /dispatch/allocate", "Step 1 of 5")

    story += section_header(S, "Overview")
    story.append(Paragraph(
        "The Dispatch Agent is the first agent in the AgentFleet pipeline. It queries available drivers "
        "and vehicles, filters by cargo weight capacity, picks the nearest vehicle using the Haversine "
        "formula, assigns a driver, creates a trip record, and sets both the vehicle and driver status to <b>Busy</b>.",
        S["body"]))

    story += section_header(S, "Responsibilities")
    story += bullet_list(S, [
        "Query available drivers and vehicles from the database.",
        "Filter vehicles by cargo weight capacity (capacity_kg ≥ cargo_weight).",
        "Select the nearest suitable vehicle to the pickup location using Haversine distance.",
        "Assign the first available driver to the selected vehicle.",
        "Create a new trip record in the database.",
        "Set assigned vehicle and driver status to <b>Busy</b>.",
    ])

    story += section_header(S, "API Endpoint")
    story += info_table(S,
        ["Method", "Path", "Description"],
        [["POST", "/dispatch/allocate", "Allocate driver and vehicle for a new delivery"]],
        [3*cm, 6*cm, 8*cm])

    story.append(Paragraph("Request Payload", S["subsection"]))
    story += code_block(S, [
        '{',
        '  "pickup":        "chennai",',
        '  "destination":   "bangalore",',
        '  "cargo_weight":  2500',
        '}',
    ])
    story.append(Paragraph("Response Payload", S["subsection"]))
    story += code_block(S, [
        '{',
        '  "status": "success",',
        '  "data": {',
        '    "trip_id":  "<uuid>",',
        '    "vehicle":  { "id": "<uuid>", "vehicle_number": "KA-01-AA-1234" },',
        '    "driver":   { "id": "<uuid>", "name": "Speedy Gonzales" }',
        '  }',
        '}',
    ])

    story += section_header(S, "Internal Logic Flow")
    story += code_block(S, [
        "allocate_dispatch(pickup, destination, cargo_weight)",
        "   │",
        "   ├── 1. get_available_drivers()         → DriverUnavailableException if none",
        "   ├── 2. get_available_vehicles()         → VehicleUnavailableException if none",
        "   ├── 3. Filter: capacity_kg >= cargo_weight",
        "   ├── 4. parse_coordinates(pickup)        → nearest vehicle via haversine_distance()",
        "   ├── 5. Assign first available driver",
        "   ├── 6. haversine_distance() + estimate_eta() → distance & duration",
        "   └── 7. create_trip() + update_vehicle_status('Busy') + update_driver_status('Busy')",
    ])

    story += section_header(S, "Module Files")
    story += info_table(S,
        ["File", "Purpose"],
        [
            ["agent.py",      "Agent registry entry — wraps service call"],
            ["service.py",    "Business logic: capacity filtering, nearest vehicle, trip creation"],
            ["repository.py", "DB queries: drivers, vehicles, trip insert, status updates"],
            ["routes.py",     "FastAPI router — POST /dispatch/allocate"],
            ["schemas.py",    "Pydantic request/response models"],
            ["prompts.py",    "AI prompt templates"],
            ["tools.py",      "LLM tool definitions"],
        ],
        [4*cm, 13*cm])

    story += section_header(S, "Shared Utilities")
    story += info_table(S,
        ["Module", "Usage"],
        [
            ["shared.geo.coordinates", "parse_coordinates() — city name → lat/lon"],
            ["shared.geo.distance",    "haversine_distance() — great-circle km"],
            ["shared.geo.eta",         "estimate_eta() — travel time at 45 km/h"],
            ["shared.exceptions",      "DriverUnavailableException, VehicleUnavailableException"],
        ],
        [7*cm, 10*cm])

    story += section_header(S, "Error Cases")
    story += info_table(S,
        ["Condition", "Exception", "HTTP Code"],
        [
            ["No drivers with Available status",           "DriverUnavailableException",  "503"],
            ["No vehicles with Available status",          "VehicleUnavailableException", "503"],
            ["No vehicle meets cargo weight requirement",  "VehicleUnavailableException", "503"],
        ],
        [7.5*cm, 5.5*cm, 4*cm])

    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph(
        "💡 To reset driver/vehicle availability during testing: GET http://localhost:8000/health/reset",
        S["body_sub"]))
    return story


def build_route(S):
    story = []
    story += cover_block(S,
        "Route Agent", "Route Intelligence", BRAND_VIOLET,
        "Computes Haversine distance, ETA, and fuel estimate for the active trip.",
        "POST /route/generate", "Step 2 of 5")

    story += section_header(S, "Overview")
    story.append(Paragraph(
        "The Route Agent is the second agent in the pipeline. It validates pickup/destination coordinates, "
        "verifies the vehicle location registry, retrieves the active trip, and computes precise routing "
        "metrics including distance, estimated travel time, and fuel consumption.",
        S["body"]))

    story += section_header(S, "Responsibilities")
    story += bullet_list(S, [
        "Validate and parse pickup and destination coordinates.",
        "Verify that the assigned vehicle has a location registry entry.",
        "Look up the active trip linked to the vehicle.",
        "Calculate Haversine great-circle distance (km).",
        "Estimate travel time using configurable speed settings.",
        "Estimate fuel consumption using a configurable rate.",
        "Update trip record status to <b>Route Generated</b>.",
    ])

    story += section_header(S, "API Endpoint")
    story += info_table(S,
        ["Method", "Path", "Description"],
        [["POST", "/route/generate", "Generate route metrics for an active trip"]],
        [3*cm, 6*cm, 8*cm])
    story.append(Paragraph("Request Payload", S["subsection"]))
    story += code_block(S, [
        '{',
        '  "vehicle_id":   "<uuid>",',
        '  "pickup":       "13.0827,80.2707",',
        '  "destination":  "12.9715,77.5945"',
        '}',
    ])
    story.append(Paragraph("Response Payload", S["subsection"]))
    story += code_block(S, [
        '{',
        '  "status": "success",',
        '  "data": {',
        '    "trip_id":           "<uuid>",',
        '    "distance_km":       347.2,',
        '    "estimated_duration":"7h 42m",',
        '    "estimated_fuel":    24.3',
        '  }',
        '}',
    ])

    story += section_header(S, "Configuration Parameters")
    story += info_table(S,
        ["Setting", "Source", "Default"],
        [
            ["ROUTE_DEFAULT_SPEED_KMH", "core/config.py", "45.0 km/h"],
            ["ROUTE_FUEL_L_PER_100KM",  "core/config.py", "7.0 L/100km"],
        ],
        [7*cm, 5*cm, 5*cm])

    story += section_header(S, "Internal Logic Flow")
    story += code_block(S, [
        "generate_route(vehicle_id, pickup, destination)",
        "   │",
        "   ├── 1. parse_coordinates(pickup)          → InvalidCoordinateException if invalid",
        "   ├── 2. parse_coordinates(destination)      → InvalidCoordinateException if invalid",
        "   ├── 3. get_vehicle_location(vehicle_id)    → VehicleUnavailableException if not found",
        "   ├── 4. get_trip(vehicle_id)                → AgentFleetException if no active trip",
        "   ├── 5. haversine_distance()                → distance_km",
        "   ├── 6. estimate_eta(distance_km, speed)    → minutes → formatted string",
        "   ├── 7. estimate_fuel(distance_km, rate)    → fuel_liters",
        "   └── 8. update_trip_route(status='Route Generated')",
    ])

    story += section_header(S, "Module Files")
    story += info_table(S,
        ["File", "Purpose"],
        [
            ["agent.py",      "Agent registry entry — wraps service call"],
            ["service.py",    "Business logic: coordinate validation, Haversine, fuel & ETA"],
            ["repository.py", "DB queries: vehicle location, active trip, route update"],
            ["routes.py",     "FastAPI router — POST /route/generate"],
            ["schemas.py",    "Pydantic request/response models"],
            ["prompts.py",    "AI prompt templates"],
            ["tools.py",      "LLM tool definitions"],
        ],
        [4*cm, 13*cm])

    story += section_header(S, "Error Cases")
    story += info_table(S,
        ["Condition", "Exception", "HTTP Code"],
        [
            ["Invalid pickup/destination coordinates", "InvalidCoordinateException",  "422"],
            ["Vehicle ID not in location registry",    "VehicleUnavailableException", "503"],
            ["No active trip found for vehicle",       "AgentFleetException",         "400"],
        ],
        [7.5*cm, 5.5*cm, 4*cm])
    return story


def build_maintenance(S):
    story = []
    story += cover_block(S,
        "Maintenance Agent", "Diagnostic Checker", BRAND_GREEN,
        "Evaluates vehicle health score, schedules servicing, and alerts the driver by email.",
        "POST /maintenance/evaluate", "Step 3 of 5")

    story += section_header(S, "Overview")
    story.append(Paragraph(
        "The Maintenance Agent is the third agent in the pipeline. It reads the vehicle's health_score, "
        "applies rule-based diagnostics, inserts maintenance logs for critical vehicles, updates database "
        "status, and sends an HTML alert email to the assigned driver.",
        S["body"]))

    story += section_header(S, "Health Score Classification")
    story += info_table(S,
        ["Score Range", "Status", "Action Taken"],
        [
            ["> 80",   "Healthy",               "Return report only"],
            ["50–80",  "Service Recommended",   "Return report + next_service_after_km"],
            ["< 50",   "Maintenance Required",  "Log inserted, vehicle → Maintenance, driver email sent"],
        ],
        [4*cm, 5.5*cm, 7.5*cm])

    story.append(Paragraph("Remaining Service Distance Formula", S["subsection"]))
    story += code_block(S, [
        "remaining_service_distance = (health_score - 50) * 50  km",
        "                             (valid when health_score >= 50)",
    ])

    story += section_header(S, "API Endpoint")
    story += info_table(S,
        ["Method", "Path", "Description"],
        [["POST", "/maintenance/evaluate", "Evaluate vehicle health and schedule maintenance if needed"]],
        [3*cm, 6*cm, 8*cm])
    story.append(Paragraph("Request Payload", S["subsection"]))
    story += code_block(S, ['{ "vehicle_id": "<uuid>" }'])
    story.append(Paragraph("Response — Healthy", S["subsection"]))
    story += code_block(S, [
        '{ "health_score": 88, "vehicle_status": "Healthy",',
        '  "message": "Vehicle is healthy.", "next_service_after_km": 1900 }',
    ])
    story.append(Paragraph("Response — Critical", S["subsection"]))
    story += code_block(S, [
        '{ "health_score": 35, "vehicle_status": "Maintenance Required",',
        '  "message": "Vehicle requires immediate maintenance." }',
    ])

    story += section_header(S, "Driver Email Alert (Critical Health)")
    story += bullet_list(S, [
        "Looks up current driver via vehicles → drivers → users JOIN.",
        "If driver email ends in @agentfleet.com (mock domain), falls back to DEMO_DRIVER_EMAIL.",
        "Sends HTML email with: health score, vehicle plate, diagnostic issue, garage instructions.",
        "Email is sent asynchronously — pipeline continues even if SMTP fails.",
    ])

    story += section_header(S, "Internal Logic Flow")
    story += code_block(S, [
        "evaluate_vehicle(vehicle_id)",
        "   │",
        "   ├── 1. get_vehicle(vehicle_id)             → VehicleUnavailableException if not found",
        "   ├── 2. get_latest_maintenance(vehicle_id)  → log trace only",
        "   ├── 3. Rule-based health_score classification",
        "   ├── 4. Compute remaining_service_distance",
        "   └── [if critical]:",
        "       ├── 5. insert_maintenance_log()",
        "       ├── 6. update_vehicle_health(status='Maintenance')",
        "       └── 7. send_email_async(driver_email, subject, html_body)",
    ])

    story += section_header(S, "Module Files")
    story += info_table(S,
        ["File", "Purpose"],
        [
            ["agent.py",      "Agent registry entry — wraps service call"],
            ["service.py",    "Business logic: health rules, maintenance log, email dispatch"],
            ["repository.py", "DB queries: vehicle fetch, log insert, health status update"],
            ["routes.py",     "FastAPI router — POST /maintenance/evaluate + GET /maintenance"],
            ["schemas.py",    "Pydantic request/response models"],
            ["prompts.py",    "AI prompt templates"],
            ["tools.py",      "LLM tool definitions"],
        ],
        [4*cm, 13*cm])
    return story


def build_analytics(S):
    story = []
    story += cover_block(S,
        "Analytics Agent", "Data Aggregator", BRAND_AMBER,
        "Aggregates fleet metrics, computes efficiency and utilization, and generates recommendations.",
        "POST /analytics/report", "Step 4 of 5")

    story += section_header(S, "Overview")
    story.append(Paragraph(
        "The Analytics Agent is the fourth agent in the pipeline. It computes trip totals, fuel efficiency, "
        "utilization percentage, and maintenance frequency for a given vehicle, then applies rule-based "
        "logic to output an actionable recommendation.",
        S["body"]))

    story += section_header(S, "Metric Formulas")
    story += info_table(S,
        ["Metric", "Formula"],
        [
            ["Fuel Efficiency", "total_distance / total_fuel  (km/L)"],
            ["Utilization %",   "min(100, (total_distance / 17000) × 100)"],
            ["100% threshold",  "17,000 km total distance = 100% fleet utilization"],
        ],
        [6*cm, 11*cm])

    story += section_header(S, "Recommendation Rules")
    story += info_table(S,
        ["Condition", "Recommendation Output"],
        [
            ["utilization < 40",                            '"Vehicle underutilized."'],
            ["maintenance_count > 5",                       '"Frequent maintenance detected."'],
            ["fuel_efficiency < fleet_avg AND fuel > 0",    '"Vehicle fuel efficiency is below fleet average."'],
            ["All other cases",                             '"Vehicle operating normally."'],
        ],
        [8*cm, 9*cm])
    story.append(Paragraph(
        "Fleet average defaults to 8.0 km/L if no historical fuel data exists in the database.",
        S["body_sub"]))

    story += section_header(S, "API Endpoints")
    story += info_table(S,
        ["Method", "Path", "Description"],
        [
            ["POST", "/analytics/report",    "Generate a performance report for a specific vehicle"],
            ["GET",  "/analytics/historical","Retrieve monthly trip-count trend data for charting"],
        ],
        [3*cm, 6*cm, 8*cm])

    story += section_header(S, "Historical Chart Logic")
    story += bullet_list(S, [
        "Queries trips table grouped by month.",
        "Uses strftime('%m', created_at) on SQLite; to_char(created_at, 'MM') on PostgreSQL.",
        "Scales trip counts: points[month] = min(100, max(50, 60 + trip_count × 8)).",
        "Falls back to static baseline [88, 72, 91, …] when no trip data exists.",
    ])

    story += section_header(S, "Internal Logic Flow")
    story += code_block(S, [
        "generate_report(vehicle_id)",
        "   │",
        "   ├── 1. get_vehicle(vehicle_id)                 → VehicleUnavailableException",
        "   ├── 2. get_trip_statistics(vehicle_id)          → total_trips, avg_distance, total_fuel",
        "   ├── 3. get_maintenance_statistics(vehicle_id)   → maintenance_count",
        "   ├── 4. get_fleet_average_fuel_efficiency()      → fleet_avg km/L",
        "   ├── 5. Compute fuel_efficiency and utilization",
        "   ├── 6. Evaluate recommendation rules",
        "   └── 7. Return structured analytics dict",
    ])

    story += section_header(S, "Module Files")
    story += info_table(S,
        ["File", "Purpose"],
        [
            ["agent.py",      "Agent registry entry — wraps service call"],
            ["service.py",    "Business logic: metric computation, utilization, recommendation rules"],
            ["repository.py", "DB queries: trip stats aggregation, maintenance count, fleet avg"],
            ["routes.py",     "FastAPI router — POST /analytics/report + GET /analytics/historical"],
            ["schemas.py",    "Pydantic request/response models"],
            ["prompts.py",    "AI prompt templates"],
            ["tools.py",      "LLM tool definitions"],
        ],
        [4*cm, 13*cm])
    return story


def build_customer(S):
    story = []
    story += cover_block(S,
        "Customer Agent", "Notifier Service", BRAND_RED,
        "Generates ETA notifications, logs alerts, and sends HTML confirmation emails to customers.",
        "POST /customer/notify", "Step 5 of 5")

    story += section_header(S, "Overview")
    story.append(Paragraph(
        "The Customer Agent is the fifth and final agent in the pipeline. It loads trip attributes, "
        "formats an ETA string, composes a customer dispatch message, logs it in the notifications table, "
        "and sends a rich HTML email with a Google Maps tracking link.",
        S["body"]))

    story += section_header(S, "Responsibilities")
    story += bullet_list(S, [
        "Fetch trip details (source, destination, estimated_duration).",
        "Retrieve assigned driver name and phone number.",
        "Retrieve assigned vehicle plate number.",
        "Format ETA string from estimated_duration minutes.",
        "Compose customer dispatch message.",
        "Insert notification log into the notifications table (type: Dispatch_Notice).",
        "Send HTML email to customer with Google Maps tracking link.",
    ])

    story += section_header(S, "Email Content")
    story += info_table(S,
        ["Email Field", "Content"],
        [
            ["Origin",          "Source city / location"],
            ["Destination",     "Destination city / location"],
            ["Route Distance",  "Distance in km"],
            ["ETA",             "Estimated arrival time (e.g., 7h 42m)"],
            ["Driver Name",     "Assigned driver full name"],
            ["Driver Phone",    "Contact phone number"],
            ["Vehicle Plate",   "Vehicle registration number"],
            ["Tracking Button", "Google Maps directions link"],
        ],
        [5*cm, 12*cm])

    story += section_header(S, "API Endpoint")
    story += info_table(S,
        ["Method", "Path", "Description"],
        [["POST", "/customer/notify", "Generate and send customer delivery notification"]],
        [3*cm, 6*cm, 8*cm])
    story.append(Paragraph("Request Payload", S["subsection"]))
    story += code_block(S, ['{ "trip_id": "<uuid>" }'])
    story.append(Paragraph("Response Payload", S["subsection"]))
    story += code_block(S, [
        '{',
        '  "status": "success",',
        '  "data": {',
        '    "trip_id":          "<uuid>",',
        '    "customer_message": "Your shipment has been dispatched. Driver Speedy...",',
        '    "notification_type":"Trip Update"',
        '  }',
        '}',
    ])

    story += section_header(S, "Internal Logic Flow")
    story += code_block(S, [
        "notify_customer(trip_id)",
        "   │",
        "   ├── 1. get_trip(trip_id)                  → AgentFleetException if not found",
        "   ├── 2. get_driver(driver_id)              → name, phone",
        "   ├── 3. get_vehicle(vehicle_id)            → vehicle_number",
        "   ├── 4. Format eta_str from estimated_duration minutes",
        "   ├── 5. Compose customer_message string",
        "   ├── 6. insert_notification(Dispatch_Notice)",
        "   └── 7. send_email_async(customer_email, html_body)",
    ])

    story += section_header(S, "Module Files")
    story += info_table(S,
        ["File", "Purpose"],
        [
            ["agent.py",      "Agent registry entry — wraps service call"],
            ["service.py",    "Business logic: message construction, notification log, email"],
            ["repository.py", "DB queries: trip, driver, vehicle fetch, notification insert"],
            ["routes.py",     "FastAPI router — POST /customer/notify"],
            ["schemas.py",    "Pydantic request/response models"],
            ["prompts.py",    "AI prompt templates"],
            ["tools.py",      "LLM tool definitions"],
        ],
        [4*cm, 13*cm])

    story += section_header(S, "Error Cases")
    story += info_table(S,
        ["Condition", "Exception", "HTTP Code"],
        [
            ["Trip not found by trip_id",    "AgentFleetException", "400"],
            ["Notification insert failure",  "Exception re-raised",  "500"],
            ["Email delivery failure",       "Warning logged only",  "—"],
        ],
        [7*cm, 5*cm, 5*cm])
    return story


def build_supervisor(S):
    story = []
    story += cover_block(S,
        "Supervisor Agent", "Orchestration Layer", BRAND_VIOLET,
        "Parses natural language commands via Groq LLM and orchestrates the full multi-agent pipeline.",
        "POST /supervisor/chat", "Orchestrator")

    story += section_header(S, "Overview")
    story.append(Paragraph(
        "The Supervisor Agent sits above all five domain agents. It provides a chat interface that accepts "
        "free-form natural language delivery instructions, uses the Groq AI model to extract structured "
        "intent, maps city names to coordinates, and routes execution to the correct workflow. "
        "It also maintains per-session conversation memory and tracks end-to-end execution latency.",
        S["body"]))

    story += section_header(S, "API Endpoints")
    story += info_table(S,
        ["Method", "Path", "Description"],
        [
            ["POST", "/supervisor/chat",    "Send a natural language command to trigger a workflow"],
            ["POST", "/supervisor/execute", "Directly execute a named workflow with structured params"],
            ["GET",  "/supervisor/status",  "Get supervisor and registered agent status"],
        ],
        [3*cm, 6*cm, 8*cm])

    story += section_header(S, "LLM Intent JSON Schema")
    story += code_block(S, [
        '{',
        '  "intent":         "dispatch | complete_trip | maintenance_status | agent_status | general",',
        '  "workflow":       "fleet_delivery | complete_trip | vehicle_maintenance | ...",',
        '  "pickup":         "string (optional) — origin city or lat,lon",',
        '  "destination":    "string (optional) — destination city or lat,lon",',
        '  "weight":         "number (optional) — cargo weight kg",',
        '  "vehicle_number": "string (optional) — registration plate"',
        '}',
    ])

    story += section_header(S, "City → Coordinate Resolver")
    story += info_table(S,
        ["City Name", "Resolved Coordinate"],
        [
            ["chennai",              "13.0827, 80.2707"],
            ["coimbatore",           "11.0168, 76.9558"],
            ["bangalore / bengaluru","12.9715, 77.5945"],
            ["mumbai",               "19.0760, 72.8777"],
            ["delhi",                "28.6139, 77.2090"],
        ],
        [7*cm, 10*cm])

    story += section_header(S, "Supported Workflows")
    story += info_table(S,
        ["Workflow Key", "Description", "Agents Triggered"],
        [
            ["fleet_delivery",      "Full end-to-end cargo dispatch",          "Dispatch → Route → Maintenance → Analytics → Customer"],
            ["complete_trip",       "Mark trip as completed, update statuses", "Trip completion sub-flow"],
            ["vehicle_maintenance", "Trigger maintenance check for a vehicle", "Maintenance Agent"],
            ["agent_status",        "Return live agent registry status",       "Status-only"],
            ["general",             "General query answered by LLM directly",  "LLM response only"],
        ],
        [4.5*cm, 5.5*cm, 7*cm])

    story += section_header(S, "Internal Logic Flow")
    story += code_block(S, [
        "chat_workflow(message)",
        "   │",
        "   ├── 1. LLMFactory.get('groq')            → resolve Groq adapter",
        "   ├── 2. memory.add('system', prompt)       → append to conversation",
        "   ├── 3. memory.add('user', message)        → append user turn",
        "   ├── 4. groq_adapter.complete(messages)    → get JSON intent string",
        "   ├── 5. Parse JSON intent → workflow, pickup, destination, weight",
        "   ├── 6. resolve_location(pickup/destination) → city → lat,lon",
        "   ├── 7. get_workflow(workflow_key)          → load from registry",
        "   ├── 8. workflow.run(db, params)            → execute pipeline",
        "   └── 9. Return results + execution_time_ms",
    ])

    story += section_header(S, "Module Files")
    story += info_table(S,
        ["File", "Purpose"],
        [
            ["agent.py",   "Agent registry entry"],
            ["service.py", "Orchestration: LLM parsing, workflow routing, response formatting"],
            ["routes.py",  "FastAPI router — /supervisor/chat, /supervisor/execute, /supervisor/status"],
            ["schemas.py", "Pydantic request/response models"],
            ["prompts.py", "System prompt templates for the LLM"],
            ["tools.py",   "LLM function-call tool definitions"],
        ],
        [4*cm, 13*cm])

    story += section_header(S, "Error Cases")
    story += info_table(S,
        ["Condition", "Exception", "HTTP Code"],
        [
            ["Groq adapter fails to load", "Exception re-raised",   "500"],
            ["LLM returns malformed JSON", "AIParserException",      "422"],
            ["Unknown workflow key",       "AgentFleetException",    "400"],
            ["Sub-agent pipeline failure", "Exception from sub-agent","Varies"],
        ],
        [7*cm, 5*cm, 5*cm])
    return story


# ═══════════════════════════════════════════════════════════════════════════════
# PDF writer
# ═══════════════════════════════════════════════════════════════════════════════

AGENTS = [
    ("dispatch",    build_dispatch,    "Dispatch Agent"),
    ("route",       build_route,       "Route Agent"),
    ("maintenance", build_maintenance, "Maintenance Agent"),
    ("analytics",   build_analytics,   "Analytics Agent"),
    ("customer",    build_customer,    "Customer Agent"),
    ("supervisor",  build_supervisor,  "Supervisor Agent"),
]

BASE_DIR = os.path.join(os.path.dirname(__file__),
    "backend", "app", "agents")

def generate_all():
    S = make_styles()
    for folder, builder, title in AGENTS:
        docs_dir = os.path.join(BASE_DIR, folder, "docs")
        os.makedirs(docs_dir, exist_ok=True)
        out_path = os.path.join(docs_dir, f"{folder}_agent.pdf")

        doc = SimpleDocTemplate(
            out_path,
            pagesize=A4,
            leftMargin=2*cm, rightMargin=2*cm,
            topMargin=2.2*cm, bottomMargin=2.2*cm,
            title=title,
            author="AgentFleet — Auto-Generated Documentation",
        )

        def make_footer(canvas, doc):
            canvas.saveState()
            canvas.setFont("Helvetica", 8)
            canvas.setFillColor(GREY_MID)
            canvas.drawCentredString(A4[0]/2, 1.2*cm,
                f"AgentFleet · {title} · Page {doc.page}")
            canvas.restoreState()

        story = builder(S)
        doc.build(story, onFirstPage=make_footer, onLaterPages=make_footer)
        print(f"[OK] Generated: {out_path}")

if __name__ == "__main__":
    generate_all()
    print("\nAll 6 agent PDF documents created successfully.")
