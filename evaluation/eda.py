import pandas as pd
import matplotlib.pyplot as plt


# -----------------------------
# Load data
# -----------------------------

df = pd.read_csv("data/transactions.csv")

print("=" * 60)
print("RecoverR - Exploratory Data Analysis")
print("=" * 60)


# -----------------------------
# Basic information
# -----------------------------

print("\nDataset Shape:")
print(df.shape)

print("\nData Types:")
print(df.dtypes)

print("\nMissing Values:")
print(df.isnull().sum())

print("\nDuplicate Rows:")
print(df.duplicated().sum())


# -----------------------------
# Target distribution
# -----------------------------

print("\nRecovery Distribution:")
print(df["recovered"].value_counts())

print("\nRecovery Percentage:")
print(df["recovered"].value_counts(normalize=True) * 100)


# -----------------------------
# Failure reason analysis
# -----------------------------

print("\nRecovery Rate by Failure Reason:")

failure_analysis = (
    df.groupby("failure_reason")["recovered"]
    .agg(["count", "sum", "mean"])
    .sort_values("mean", ascending=False)
)

failure_analysis.columns = [
    "total_transactions",
    "recovered_transactions",
    "recovery_rate"
]

print(failure_analysis)


# -----------------------------
# Retry count analysis
# -----------------------------

print("\nRecovery Rate by Retry Count:")

retry_analysis = (
    df.groupby("retry_count")["recovered"]
    .agg(["count", "mean"])
)

retry_analysis.columns = [
    "transactions",
    "recovery_rate"
]

print(retry_analysis)


# -----------------------------
# Payment method analysis
# -----------------------------

print("\nRecovery Rate by Payment Method:")

payment_analysis = (
    df.groupby("payment_method")["recovered"]
    .agg(["count", "mean"])
)

payment_analysis.columns = [
    "transactions",
    "recovery_rate"
]

print(payment_analysis)


# -----------------------------
# Risk score analysis
# -----------------------------

df["risk_bucket"] = pd.cut(
    df["risk_score"],
    bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
    labels=[
        "0-0.2",
        "0.2-0.4",
        "0.4-0.6",
        "0.6-0.8",
        "0.8-1.0"
    ],
    include_lowest=True
)

print("\nRecovery Rate by Risk Bucket:")

risk_analysis = (
    df.groupby(
        "risk_bucket",
        observed=True
    )["recovered"]
    .agg(["count", "mean"])
)

risk_analysis.columns = [
    "transactions",
    "recovery_rate"
]

print(risk_analysis)


# -----------------------------
# Customer history
# -----------------------------

df["historical_success_rate"] = (
    df["previous_successful_transactions"]
    /
    df["previous_transactions"].replace(0, 1)
)

print("\nHistorical Success Rate Statistics:")

print(
    df["historical_success_rate"].describe()
)


# -----------------------------
# Amount statistics
# -----------------------------

print("\nTransaction Amount Statistics:")

print(
    df["amount"].describe()
)


# -----------------------------
# Correlation
# -----------------------------

numeric_columns = [
    "amount",
    "retry_count",
    "previous_transactions",
    "previous_successful_transactions",
    "risk_score",
    "historical_success_rate",
    "recovered"
]

print("\nNumeric Correlation with Recovery:")

correlation = (
    df[numeric_columns]
    .corr()["recovered"]
    .sort_values(ascending=False)
)

print(correlation)


# -----------------------------
# Visualizations
# -----------------------------

plt.figure(figsize=(10, 6))

failure_analysis["recovery_rate"].plot(
    kind="bar"
)

plt.title("Recovery Rate by Failure Reason")
plt.ylabel("Recovery Rate")
plt.xlabel("Failure Reason")
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig(
    "evaluation/recovery_by_failure.png"
)

plt.close()


plt.figure(figsize=(8, 5))

retry_analysis["recovery_rate"].plot(
    kind="bar"
)

plt.title("Recovery Rate by Retry Count")
plt.ylabel("Recovery Rate")
plt.xlabel("Retry Count")
plt.tight_layout()

plt.savefig(
    "evaluation/recovery_by_retry.png"
)

plt.close()


plt.figure(figsize=(8, 5))

risk_analysis["recovery_rate"].plot(
    kind="bar"
)

plt.title("Recovery Rate by Risk Score")
plt.ylabel("Recovery Rate")
plt.xlabel("Risk Bucket")
plt.tight_layout()

plt.savefig(
    "evaluation/recovery_by_risk.png"
)

plt.close()


print("\nEDA completed successfully.")

print("\nCharts saved to:")
print("evaluation/recovery_by_failure.png")
print("evaluation/recovery_by_retry.png")
print("evaluation/recovery_by_risk.png")