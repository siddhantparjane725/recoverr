from backend.models.schemas import Transaction


RETRYABLE_FAILURES = {
    "bank_timeout",
    "network_error",
    "temporary_bank_failure",
    "gateway_timeout",
}


CUSTOMER_ACTION_FAILURES = {
    "insufficient_funds",
    "expired_card",
    "invalid_card",
}


PERMANENT_FAILURES = {
    "account_closed",
    "card_blocked",
}


def diagnose_failure(transaction: Transaction):

    reason = transaction.failure_reason

    if reason in RETRYABLE_FAILURES:
        return {
            "category": "temporary",
            "recoverable": True,
            "recommended_action": "retry",
        }

    if reason in CUSTOMER_ACTION_FAILURES:
        return {
            "category": "customer_action_required",
            "recoverable": True,
            "recommended_action": "notify_customer",
        }

    if reason in PERMANENT_FAILURES:
        return {
            "category": "permanent",
            "recoverable": False,
            "recommended_action": "stop",
        }

    return {
        "category": "unknown",
        "recoverable": False,
        "recommended_action": "escalate",
    }