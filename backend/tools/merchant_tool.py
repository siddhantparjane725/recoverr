from datetime import datetime


def request_merchant_approval(transaction):

    return {
        "transaction_id": transaction["transaction_id"],
        "status": "approval_required",
        "action": "request_merchant_approval",
        "message": (
            "Merchant approval required before recovery action"
        ),
        "timestamp": datetime.utcnow().isoformat()
    }