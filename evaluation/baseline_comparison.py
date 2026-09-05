import pandas as pd
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

TEST_PATH = ROOT / "evaluation" / "results" / "test_predictions.csv"


TEMPORARY_FAILURES = {
    "bank_timeout",
    "network_error",
    "temporary_bank_failure",
    "gateway_timeout",
}


def run_baseline():

    df = pd.read_csv(TEST_PATH)

    baseline_attempts = 0
    baseline_successes = 0
    baseline_revenue = 0.0

    recoverr = pd.read_csv(
        ROOT / "evaluation" / "results" / "batch_recovery_results.csv"
    )

    recoverr_revenue = recoverr["recovered_amount"].sum()
    recoverr_attempts = (recoverr["action"] == "retry").sum()
    recoverr_successes = recoverr["successful_recovery"].sum()

    for _, row in df.iterrows():

        failure_reason = row["failure_reason"]
        retry_count = int(row["retry_count"])
        amount = float(row["amount"])
        risk_score = float(row["risk_score"])

        # Simple rule-based baseline:
        #
        # Retry temporary failures if:
        # - retry count < 2
        # - amount <= ₹5,000
        # - risk score < 0.70
        #
        # No ML involved.

        should_retry = (
            failure_reason in TEMPORARY_FAILURES
            and retry_count < 2
            and amount <= 5000
            and risk_score < 0.70
        )

        if should_retry:

            baseline_attempts += 1

            if bool(row["actual_recovered"]):

                baseline_successes += 1
                baseline_revenue += amount

    baseline_success_rate = (
        baseline_successes / baseline_attempts
        if baseline_attempts
        else 0
    )

    print()
    print("=" * 70)
    print("                 RECOVERR vs BASELINE")
    print("=" * 70)

    print()
    print("SIMPLE RULE-BASED BASELINE")
    print("-" * 70)

    print(f"Recovery attempts       : {baseline_attempts:,}")
    print(f"Successful recoveries   : {baseline_successes:,}")
    print(
        f"Success rate            : "
        f"{baseline_success_rate * 100:.2f}%"
    )
    print(f"Revenue recovered       : ₹{baseline_revenue:,.2f}")

    print()
    print("RECOVERR ML STRATEGY")
    print("-" * 70)

    print(f"Recovery attempts       : {recoverr_attempts:,}")
    print(f"Successful recoveries   : {recoverr_successes:,}")
    print(
        f"Success rate            : "
        f"{(recoverr_successes / recoverr_attempts * 100):.2f}%"
    )
    print(f"Revenue recovered       : ₹{recoverr_revenue:,.2f}")

    print()
    print("IMPACT")
    print("-" * 70)

    revenue_difference = recoverr_revenue - baseline_revenue
    attempt_difference = recoverr_attempts - baseline_attempts

    print(
        f"Revenue difference      : "
        f"₹{revenue_difference:,.2f}"
    )

    print(
        f"Attempt difference      : "
        f"{attempt_difference:+,}"
    )

    if baseline_revenue > 0:

        revenue_change = (
            revenue_difference / baseline_revenue
        ) * 100

        print(
            f"Revenue change          : "
            f"{revenue_change:+.2f}%"
        )

    print("=" * 70)


if __name__ == "__main__":
    run_baseline()