from datetime import datetime
from pathlib import Path
import json

from backend.tools.payment_tool import retry_payment
from backend.tools.notification_tool import notify_customer


# ---------------------------------------------------------
# AUDIT LOG
# ---------------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / "evaluation" / "results"
AUDIT_PATH = AUDIT_DIR / "audit_log.jsonl"

AUDIT_DIR.mkdir(parents=True, exist_ok=True)


def write_audit_log(record: dict):
    """
    Append one agent decision/execution to the audit log.
    """

    with open(AUDIT_PATH, "a", encoding="utf-8") as file:
        file.write(
            json.dumps(record, ensure_ascii=False)
            + "\n"
        )


# ---------------------------------------------------------
# PAYMENT VERIFICATION
# ---------------------------------------------------------

def verify_payment(transaction):
    """
    Simulated payment verification.

    In a production Razorpay integration this would query
    the payment/order status through the payment API.

    For this buildathon project we use test-mode simulation.
    """

    # The transaction object can be marked as recovered
    # by the simulated payment tool.
    if getattr(transaction, "payment_recovered", False):
        return {
            "verified": True,
            "status": "recovered",
            "message": "Payment status verified successfully."
        }

    return {
        "verified": False,
        "status": "failed",
        "message": "Payment could not be verified as recovered."
    }


# ---------------------------------------------------------
# RECOVERY EXECUTION
# ---------------------------------------------------------

def execute_recovery(transaction, decision):
    """
    Execute the action selected by RecoverR.

    Flow:

        Decision
           ↓
        Execute
           ↓
        Verify
           ↓
        Audit
    """

    action = decision.get("action")

    timestamp = datetime.utcnow().isoformat() + "Z"

    execution = {
        "transaction_id": transaction.transaction_id,
        "timestamp": timestamp,
        "action": action,
        "decision_reason": decision.get("reason", ""),
        "recovery_probability": decision.get(
            "recovery_probability",
            0.0
        ),
        "expected_recovery_value": decision.get(
            "expected_recovery_value",
            0.0
        ),
        "execution_status": "not_executed",
        "verification_status": "not_verified",
        "recovered_amount": 0.0,
    }

    # -----------------------------------------------------
    # RETRY PAYMENT
    # -----------------------------------------------------

    if action == "retry":

        result = retry_payment(transaction)

        # Store simulated result on transaction
        if isinstance(result, dict):

            success = result.get(
                "success",
                False
            )

            transaction.payment_recovered = success

        else:

            success = bool(result)

            transaction.payment_recovered = success

        if success:

            execution["execution_status"] = "success"

        else:

            execution["execution_status"] = "failed"

        # -------------------------------------------------
        # VERIFY
        # -------------------------------------------------

        verification = verify_payment(transaction)

        if verification["verified"]:

            execution["verification_status"] = "verified"

            execution["recovered_amount"] = float(
                transaction.amount
            )

        else:

            execution["verification_status"] = "failed"

    # -----------------------------------------------------
    # CUSTOMER NOTIFICATION
    # -----------------------------------------------------

    elif action == "notify_customer":

        result = notify_customer(transaction)

        execution["execution_status"] = "success"

        execution["verification_status"] = "not_required"

        execution["message"] = (
            result.get("message", "Customer notified.")
            if isinstance(result, dict)
            else "Customer notification sent."
        )

    # -----------------------------------------------------
    # MERCHANT APPROVAL
    # -----------------------------------------------------

    elif action == "request_approval":

        execution["execution_status"] = "pending_approval"

        execution["verification_status"] = "not_required"

        execution["message"] = (
            "Merchant approval required before recovery."
        )

    # -----------------------------------------------------
    # STOP / ESCALATE
    # -----------------------------------------------------

    elif action in ["stop", "escalate"]:

        execution["execution_status"] = "blocked"

        execution["verification_status"] = "not_required"

        execution["message"] = (
            "Recovery action stopped by policy."
        )

    # -----------------------------------------------------
    # UNKNOWN ACTION
    # -----------------------------------------------------

    else:

        execution["execution_status"] = "rejected"

        execution["verification_status"] = "not_required"

        execution["message"] = (
            f"Unknown recovery action: {action}"
        )

    # -----------------------------------------------------
    # AUDIT
    # -----------------------------------------------------

    write_audit_log(execution)

    return execution