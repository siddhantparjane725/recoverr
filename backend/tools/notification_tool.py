from datetime import datetime


def notify_customer(transaction):

    return {
        "transaction_id": transaction["transaction_id"],
        "status": "notification_sent",
        "action": "notify_customer",
        "message": (
            "Customer recovery notification generated"
        ),
        "timestamp": datetime.utcnow().isoformat()
    }