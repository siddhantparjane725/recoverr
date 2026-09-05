from backend.models.schemas import Transaction


MAX_AUTO_RETRY_AMOUNT = 5000
MAX_RETRY_COUNT = 2
MAX_RISK_SCORE = 0.7


def check_policy(transaction: Transaction, proposed_action: str):

    if transaction.risk_score >= MAX_RISK_SCORE:
        return {
            "allowed": False,
            "reason": "Transaction risk score exceeds safety threshold",
            "action": "escalate",
        }

    if transaction.retry_count >= MAX_RETRY_COUNT:
        return {
            "allowed": False,
            "reason": "Maximum retry count reached",
            "action": "stop",
        }

    if (
        proposed_action == "retry"
        and transaction.amount > MAX_AUTO_RETRY_AMOUNT
    ):
        return {
            "allowed": False,
            "reason": "High-value transaction requires merchant approval",
            "action": "request_approval",
        }

    return {
        "allowed": True,
        "reason": "Action satisfies recovery policy",
        "action": proposed_action,
    }