import random


def retry_payment(transaction):
    """
    Simulated payment retry tool.

    In production this would call the Razorpay payment API.
    For the buildathon demo, we simulate the retry outcome.
    """

    transaction_id = transaction.transaction_id
    amount = transaction.amount

    # Simulate a payment retry.
    # Higher historical success rate gives a better chance of recovery.
    historical_success_rate = (
        transaction.previous_successful_transactions
        / max(transaction.previous_transactions, 1)
    )

    # Temporary failures are generally retryable.
    base_probability = 0.60

    # Give customers with good payment history a small advantage.
    success_probability = min(
        0.90,
        base_probability + (historical_success_rate * 0.20)
    )

    success = random.random() < success_probability

    return {
        "success": success,
        "transaction_id": transaction_id,
        "amount": amount,
        "message": (
            "Payment recovered successfully."
            if success
            else "Payment retry failed."
        )
    }