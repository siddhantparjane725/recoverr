import joblib
import pandas as pd


MODEL_PATH = "backend/ml/recovery_model.joblib"


model = joblib.load(MODEL_PATH)


FEATURES = [
    "amount",
    "payment_method",
    "bank",
    "failure_reason",
    "retry_count",
    "previous_transactions",
    "previous_successful_transactions",
    "risk_score",
    "historical_success_rate",
    "high_value_transaction"
]


def predict_recovery(transaction):

    historical_success_rate = (
        transaction.previous_successful_transactions
        /
        max(transaction.previous_transactions, 1)
    )

    high_value_transaction = int(
        transaction.amount > 10000
    )

    data = pd.DataFrame([{
        "amount": transaction.amount,
        "payment_method": transaction.payment_method,
        "bank": transaction.bank,
        "failure_reason": transaction.failure_reason,
        "retry_count": transaction.retry_count,
        "previous_transactions": transaction.previous_transactions,
        "previous_successful_transactions":
            transaction.previous_successful_transactions,
        "risk_score": transaction.risk_score,
        "historical_success_rate":
            historical_success_rate,
        "high_value_transaction":
            high_value_transaction
    }])

    probability = model.predict_proba(data)[0][1]

    return float(probability)