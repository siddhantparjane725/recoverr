import numpy as np
import pandas as pd

np.random.seed(42)

N = 10000

payment_methods = ["card", "upi", "netbanking", "wallet"]

banks = [
    "HDFC",
    "ICICI",
    "SBI",
    "AXIS",
    "KOTAK"
]

failure_reasons = [
    "bank_timeout",
    "network_error",
    "temporary_bank_failure",
    "gateway_timeout",
    "insufficient_funds",
    "expired_card",
    "invalid_card",
    "account_closed",
    "card_blocked"
]


data = pd.DataFrame({

    "transaction_id": [
        f"pay_{i:06d}" for i in range(N)
    ],

    "customer_id": [
        f"cust_{np.random.randint(1, 3000):05d}"
        for _ in range(N)
    ],

    "amount": np.round(
        np.random.lognormal(
            mean=7.5,
            sigma=0.8,
            size=N
        ),
        2
    ),

    "payment_method": np.random.choice(
        payment_methods,
        N,
        p=[0.45, 0.35, 0.15, 0.05]
    ),

    "bank": np.random.choice(
        banks,
        N
    ),

    "failure_reason": np.random.choice(
        failure_reasons,
        N,
        p=[
            0.15,
            0.12,
            0.10,
            0.08,
            0.18,
            0.10,
            0.08,
            0.10,
            0.09
        ]
    ),

    "retry_count": np.random.randint(
        0,
        3,
        N
    ),

    "previous_transactions": np.random.randint(
        0,
        20,
        N
    ),

    "previous_successful_transactions": np.random.randint(
        0,
        20,
        N
    ),

    "risk_score": np.round(
        np.random.beta(
            2,
            8,
            N
        ),
        3
    )
})


# Make successful transactions logically consistent
data["previous_successful_transactions"] = np.minimum(
    data["previous_successful_transactions"],
    data["previous_transactions"]
)


# Determine whether recovery is possible
temporary_failure = data["failure_reason"].isin([
    "bank_timeout",
    "network_error",
    "temporary_bank_failure",
    "gateway_timeout"
])

customer_recoverable = data["failure_reason"].isin([
    "insufficient_funds",
    "expired_card",
    "invalid_card"
])


historical_success_rate = np.where(
    data["previous_transactions"] > 0,

    data["previous_successful_transactions"]
    / data["previous_transactions"],

    0.5
)


# Calculate probability of recovery
probability = (
    0.20
    + 0.35 * temporary_failure
    + 0.15 * customer_recoverable
    + 0.20 * historical_success_rate
    - 0.12 * data["retry_count"]
    - 0.25 * data["risk_score"]
    - 0.10 * (data["amount"] > 10000)
)


probability = np.clip(
    probability,
    0.02,
    0.98
)


# Generate actual outcome
data["recovered"] = (
    np.random.random(N) < probability
).astype(int)


# Permanent failures should almost never recover
permanent_failure = data["failure_reason"].isin([
    "account_closed",
    "card_blocked"
])

data.loc[
    permanent_failure,
    "recovered"
] = 0


data.to_csv(
    "data/transactions.csv",
    index=False
)


print("Dataset created successfully!")
print(f"Rows: {len(data)}")
print()
print(data.head())
print()
print("Recovery distribution:")
print(data["recovered"].value_counts())