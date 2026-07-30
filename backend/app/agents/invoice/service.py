from sqlalchemy.orm import Session
from sqlalchemy import text
import uuid
import logging

logger = logging.getLogger("agentfleet.agents.invoice.service")

BASE_FEE_INR = 500.0
DISTANCE_RATE_PER_KM_INR = 12.0
GST_RATE = 0.18


class InvoiceService:
    """
    Business layer for Invoice Agent.
    Generates a cost-breakdown invoice, stores it in DB, and emails it to the customer.
    """

    def generate_invoice(
        self,
        db: Session,
        trip_id: str,
        distance_km: float,
        fuel_cost_inr: float,
    ) -> dict:
        """
        Calculates invoice totals, persists to DB, and triggers email delivery.
        """
        logger.info(f"Generating invoice for trip={trip_id}")

        # 1. Cost breakdown
        distance_charge = round(distance_km * DISTANCE_RATE_PER_KM_INR, 2)
        subtotal = round(BASE_FEE_INR + distance_charge + fuel_cost_inr, 2)
        gst_amount = round(subtotal * GST_RATE, 2)
        total_amount_inr = round(subtotal + gst_amount, 2)
        invoice_number = f"INV-{str(uuid.uuid4())[:8].upper()}"

        # 2. Fetch trip details for email
        customer_email = None
        source = "—"
        destination = "—"
        driver_name = "—"
        vehicle_number = "—"
        try:
            row = db.execute(text("""
                SELECT t.source, t.destination,
                       u.name as driver_name,
                       v.vehicle_number
                FROM trips t
                LEFT JOIN drivers d ON t.driver_id = d.id
                LEFT JOIN users u ON d.user_id = u.id
                LEFT JOIN vehicles v ON t.vehicle_id = v.id
                WHERE t.id = :trip_id
            """), {"trip_id": trip_id}).first()
            if row:
                source = row[0] or "—"
                destination = row[1] or "—"
                driver_name = row[2] or "—"
                vehicle_number = row[3] or "—"
        except Exception as e:
            logger.warning(f"Failed to fetch trip details for invoice: {e}")

        # 3. Persist invoice to invoices table
        invoice_id = str(uuid.uuid4())
        try:
            try:
                db.execute(text("""
                    CREATE TABLE IF NOT EXISTS invoices (
                        id TEXT PRIMARY KEY,
                        invoice_number TEXT,
                        trip_id TEXT,
                        base_fee REAL,
                        distance_charge REAL,
                        fuel_cost REAL,
                        subtotal REAL,
                        gst_amount REAL,
                        total_amount REAL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                db.commit()
            except Exception:
                pass

            db.execute(text("""
                INSERT INTO invoices (id, invoice_number, trip_id, base_fee, distance_charge,
                    fuel_cost, subtotal, gst_amount, total_amount)
                VALUES (:id, :inv_num, :trip_id, :base_fee, :dist_charge,
                    :fuel_cost, :subtotal, :gst, :total)
            """), {
                "id": invoice_id,
                "inv_num": invoice_number,
                "trip_id": trip_id,
                "base_fee": BASE_FEE_INR,
                "dist_charge": distance_charge,
                "fuel_cost": fuel_cost_inr,
                "subtotal": subtotal,
                "gst": gst_amount,
                "total": total_amount_inr,
            })
            db.commit()
            logger.info(f"Invoice {invoice_number} persisted to database.")
        except Exception as e:
            db.rollback()
            logger.warning(f"Failed to persist invoice: {e}")

        # 4. Email invoice to customer
        try:
            from backend.app.core.config import settings
            from backend.app.shared.notifications.email import send_email_async

            cust_email = settings.DEMO_CUSTOMER_EMAIL
            if cust_email:
                subject = f"[AgentFleet] Invoice {invoice_number} — Trip Delivery Charges"
                html_body = f"""
                <html>
                  <body style="font-family: Arial, sans-serif; color: #333;">
                    <div style="max-width:600px;margin:0 auto;padding:20px;border:1px solid #e0e0e0;border-radius:8px;">
                      <h2 style="color:#4f8ef7;border-bottom:2px solid #4f8ef7;padding-bottom:10px;">
                        Delivery Invoice
                      </h2>
                      <p><strong>Invoice No:</strong> {invoice_number}</p>
                      <p><strong>Route:</strong> {source} &rarr; {destination}</p>
                      <p><strong>Driver:</strong> {driver_name} &nbsp; | &nbsp; <strong>Vehicle:</strong> {vehicle_number}</p>
                      <table style="width:100%;border-collapse:collapse;margin:15px 0;">
                        <tr style="background:#f8f9fa;">
                          <td style="padding:8px;border:1px solid #ddd;font-weight:bold;">Description</td>
                          <td style="padding:8px;border:1px solid #ddd;text-align:right;font-weight:bold;">Amount (INR)</td>
                        </tr>
                        <tr><td style="padding:8px;border:1px solid #ddd;">Base Service Fee</td>
                            <td style="padding:8px;border:1px solid #ddd;text-align:right;">&#8377; {BASE_FEE_INR:.2f}</td></tr>
                        <tr><td style="padding:8px;border:1px solid #ddd;">Distance Charge ({distance_km} km @ &#8377;{DISTANCE_RATE_PER_KM_INR}/km)</td>
                            <td style="padding:8px;border:1px solid #ddd;text-align:right;">&#8377; {distance_charge:.2f}</td></tr>
                        <tr><td style="padding:8px;border:1px solid #ddd;">Fuel Cost</td>
                            <td style="padding:8px;border:1px solid #ddd;text-align:right;">&#8377; {fuel_cost_inr:.2f}</td></tr>
                        <tr><td style="padding:8px;border:1px solid #ddd;">Subtotal</td>
                            <td style="padding:8px;border:1px solid #ddd;text-align:right;">&#8377; {subtotal:.2f}</td></tr>
                        <tr><td style="padding:8px;border:1px solid #ddd;">GST (18%)</td>
                            <td style="padding:8px;border:1px solid #ddd;text-align:right;">&#8377; {gst_amount:.2f}</td></tr>
                        <tr style="background:#e8f5e9;">
                          <td style="padding:10px;border:1px solid #ddd;font-weight:bold;font-size:14px;">Total Amount</td>
                          <td style="padding:10px;border:1px solid #ddd;text-align:right;font-weight:bold;font-size:14px;color:#10b981;">&#8377; {total_amount_inr:.2f}</td>
                        </tr>
                      </table>
                      <p style="font-size:11px;color:#999;margin-top:20px;">This is an automated invoice from AgentFleet. Trip ID: {trip_id[:8]}</p>
                    </div>
                  </body>
                </html>"""
                text_body = (
                    f"Invoice {invoice_number}\nRoute: {source} to {destination}\n"
                    f"Base Fee: INR {BASE_FEE_INR}\nDistance: INR {distance_charge}\n"
                    f"Fuel: INR {fuel_cost_inr}\nGST: INR {gst_amount}\nTotal: INR {total_amount_inr}"
                )
                send_email_async(cust_email, subject, html_body, text_body)
        except Exception as e:
            logger.warning(f"Failed to send invoice email: {e}")

        return {
            "invoice_id": invoice_id,
            "invoice_number": invoice_number,
            "trip_id": trip_id,
            "base_fee_inr": BASE_FEE_INR,
            "distance_charge_inr": distance_charge,
            "fuel_cost_inr": fuel_cost_inr,
            "subtotal_inr": subtotal,
            "gst_inr": gst_amount,
            "total_amount_inr": total_amount_inr,
        }
