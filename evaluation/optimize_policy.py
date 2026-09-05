from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

VALIDATION_PATH = (
    ROOT
    / "evaluation"
    / "results"
    / "validation_predictions.csv"
)


TEMPORARY_FAILURES = {
    "bank_timeout",
    "network_error",
    "temporary_bank_failure",
    "gateway_timeout",
}


def evaluate_threshold(df, threshold):

    # Apply the SAME hard safety constraints
    # that automatic retries must respect.
    eligible = (
        df["failure_reason"].isin(TEMPORARY_FAILURES)
        & (df["retry_count"] < 2)
        & (df["amount"] <= 5000)
        & (df["risk_score"] < 0.70)
    )

    # ML decides which eligible transactions
    # are valuable enough to retry.
    selected = (
        eligible
        & (df["recovery_probability"] >= threshold)
    )

    attempted = df[selected]

    attempts = len(attempted)

    successful = int(
        attempted["actual_recovered"].sum()
    )

    revenue_recovered = float(
        attempted.loc[
            attempted["actual_recovered"] == 1,
            "amount"
        ].sum()
    )

    attempted_revenue = float(
        attempted["amount"].sum()
    )

    success_rate = (
        successful / attempts
        if attempts > 0
        else 0
    )

    avg_expected_value = (
        attempted["expected_recovery_value"].mean()
        if attempts > 0
        else 0
    )

    return {
        "threshold": threshold,
        "attempts": attempts,
        "successful_recoveries": successful,
        "success_rate": success_rate,
        "attempted_revenue": attempted_revenue,
        "revenue_recovered": revenue_recovered,
        "avg_expected_recovery_value": avg_expected_value,
    }


def main():

    df = pd.read_csv(VALIDATION_PATH)

    thresholds = [
        0.30,
        0.35,
        0.40,
        0.45,
        0.50,
        0.55,
        0.60,
        0.65,
        0.70,
        0.75,
        0.80,
    ]

    rows = []

    for threshold in thresholds:
        rows.append(
            evaluate_threshold(
                df,
                threshold
            )
        )

    results = pd.DataFrame(rows)

    results["success_rate_pct"] = (
        results["success_rate"] * 100
    )

    print()
    print("=" * 92)
    print(
        "                 RECOVERR VALIDATION POLICY OPTIMIZATION"
    )
    print("=" * 92)

    print(
        results[
            [
                "threshold",
                "attempts",
                "successful_recoveries",
                "success_rate_pct",
                "revenue_recovered",
            ]
        ].to_string(
            index=False,
            formatters={
                "threshold":
                    lambda x: f"{x:.2f}",

                "success_rate_pct":
                    lambda x: f"{x:.2f}%",

                "revenue_recovered":
                    lambda x: f"₹{x:,.2f}",
            }
        )
    )

    print("=" * 92)

    # ---------------------------------------------------
    # Business objective
    # ---------------------------------------------------
    #
    # We want high revenue recovery, but we do NOT want
    # to sacrifice recovery quality completely.
    #
    # Require at least 55% observed recovery success
    # on validation.
    # ---------------------------------------------------

    MIN_SUCCESS_RATE = 0.55

    candidates = results[
        results["success_rate"]
        >= MIN_SUCCESS_RATE
    ]

    if len(candidates) == 0:

        print(
            "\nNo threshold satisfied the minimum "
            "success-rate constraint."
        )

        return

    best = candidates.loc[
        candidates["revenue_recovered"].idxmax()
    ]

    print()
    print("SELECTED POLICY")
    print("-" * 92)

    print(
        f"Minimum required success rate : "
        f"{MIN_SUCCESS_RATE * 100:.0f}%"
    )

    print(
        f"Selected retry threshold      : "
        f"{best['threshold']:.2f}"
    )

    print(
        f"Validation attempts           : "
        f"{int(best['attempts']):,}"
    )

    print(
        f"Validation successes          : "
        f"{int(best['successful_recoveries']):,}"
    )

    print(
        f"Validation success rate       : "
        f"{best['success_rate'] * 100:.2f}%"
    )

    print(
        f"Validation revenue recovered  : "
        f"₹{best['revenue_recovered']:,.2f}"
    )

    print("=" * 92)

    output_path = (
        ROOT
        / "evaluation"
        / "results"
        / "policy_threshold_analysis.csv"
    )

    results.to_csv(
        output_path,
        index=False
    )

    print()
    print("Threshold analysis saved to:")
    print(output_path)


if __name__ == "__main__":
    main()