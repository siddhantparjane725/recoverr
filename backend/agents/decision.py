from backend.models.schemas import Transaction
from backend.agents.diagnosis import diagnose_failure
from backend.policies.guardrails import check_policy
from backend.services.ml_predictor import predict_recovery


# Selected using the validation set.
# Do NOT tune this using the final test set.
RETRY_PROBABILITY_THRESHOLD = 0.30


def make_recovery_decision(transaction: Transaction):

    diagnosis = diagnose_failure(transaction)

    # --------------------------------------------------
    # Permanent / unknown failure
    # --------------------------------------------------

    if not diagnosis["recoverable"]:

        return {
            "transaction_id": transaction.transaction_id,
            "recoverable": False,
            "recovery_probability": 0.0,
            "expected_recovery_value": 0.0,
            "action": diagnosis["recommended_action"],
            "reason": f"Failure classified as {diagnosis['category']}"
        }

    # --------------------------------------------------
    # ML recovery probability
    # --------------------------------------------------

    recovery_probability = predict_recovery(
        transaction
    )

    expected_recovery_value = (
        transaction.amount
        * recovery_probability
    )

    # --------------------------------------------------
    # Action selection
    # --------------------------------------------------

    if diagnosis["category"] == "temporary":

        if recovery_probability >= RETRY_PROBABILITY_THRESHOLD:
            proposed_action = "retry"
        else:
            proposed_action = "escalate"

    elif diagnosis["category"] == "customer_action_required":

        if recovery_probability >= RETRY_PROBABILITY_THRESHOLD:
            proposed_action = "notify_customer"
        else:
            proposed_action = "escalate"

    else:

        proposed_action = diagnosis["recommended_action"]

    # --------------------------------------------------
    # Safety policy
    # --------------------------------------------------

    policy = check_policy(
        transaction,
        proposed_action
    )

    return {
        "transaction_id": transaction.transaction_id,
        "recoverable": True,
        "recovery_probability": round(
            recovery_probability,
            4
        ),
        "expected_recovery_value": round(
            expected_recovery_value,
            2
        ),
        "action": policy["action"],
        "reason": policy["reason"]
    }