import sys
from pathlib import Path

# ---------------------------------------------------------
# PROJECT PATH
# ---------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd

from backend.models.schemas import Transaction
from backend.agents.decision import make_recovery_decision


# ---------------------------------------------------------
# FILE PATHS
# ---------------------------------------------------------

TEST_PATH = ROOT / "evaluation" / "results" / "test_predictions.csv"
OUTPUT_PATH = ROOT / "evaluation" / "results" / "batch_recovery_results.csv"


# ---------------------------------------------------------
# TRANSACTION BUILDER
# ---------------------------------------------------------

def build_transaction(row, index):
    """
    Convert a test-set row into the Transaction schema.

    IMPORTANT:
    actual_recovered is NOT passed into the transaction.
    This prevents test-set leakage into the agent decision.
    """

    return Transaction(
        transaction_id=f"test_{index}",
        customer_id=f"customer_{index}",
        amount=float(row["amount"]),
        payment_method=row["payment_method"],
        bank=row["bank"],
        status="failed",
        failure_reason=row["failure_reason"],
        retry_count=int(row["retry_count"]),
        previous_transactions=int(row["previous_transactions"]),
        previous_successful_transactions=int(
            row["previous_successful_transactions"]
        ),
        risk_score=float(row["risk_score"]),
    )


# ---------------------------------------------------------
# MAIN EVALUATION
# ---------------------------------------------------------

def run_batch():

    # -----------------------------------------------------
    # LOAD HELD-OUT TEST DATA
    # -----------------------------------------------------

    if not TEST_PATH.exists():
        raise FileNotFoundError(
            f"Test prediction file not found:\n{TEST_PATH}"
        )

    df = pd.read_csv(TEST_PATH)

    total_transactions = len(df)

    # -----------------------------------------------------
    # CORE METRICS
    # -----------------------------------------------------

    total_failed_revenue = 0.0

    potentially_recoverable_revenue = 0.0
    automatically_actionable_revenue = 0.0

    recovery_attempts = 0
    successful_recoveries = 0

    revenue_recovered = 0.0

    # -----------------------------------------------------
    # ACTION COUNTS
    # -----------------------------------------------------

    retry_actions = 0
    customer_notifications = 0
    merchant_escalations = 0
    blocked_actions = 0

    # -----------------------------------------------------
    # SAFETY METRICS
    # -----------------------------------------------------

    high_risk_blocked = 0
    retry_limit_blocked = 0
    high_value_escalations = 0

    # -----------------------------------------------------
    # RESULTS
    # -----------------------------------------------------

    results = []

    # -----------------------------------------------------
    # PROCESS EACH TRANSACTION
    # -----------------------------------------------------

    for index, row in df.iterrows():

        transaction = build_transaction(row, index)

        total_failed_revenue += transaction.amount

        # -------------------------------------------------
        # AGENT DECISION
        # -------------------------------------------------
        # actual_recovered is NOT available here.
        # The decision is based only on transaction data,
        # ML prediction, diagnosis and guardrails.
        # -------------------------------------------------

        decision = make_recovery_decision(transaction)

        action = decision["action"]

        recoverable = bool(
            decision.get("recoverable", False)
        )

        recovery_probability = float(
            decision.get("recovery_probability", 0.0)
        )

        expected_recovery_value = float(
            decision.get("expected_recovery_value", 0.0)
        )

        # -------------------------------------------------
        # POTENTIALLY RECOVERABLE REVENUE
        # -------------------------------------------------

        if recoverable:
            potentially_recoverable_revenue += transaction.amount

        # -------------------------------------------------
        # AUTOMATICALLY ACTIONABLE REVENUE
        # -------------------------------------------------

        automatically_actionable = action == "retry"

        if automatically_actionable:
            automatically_actionable_revenue += transaction.amount

        # -------------------------------------------------
        # ACTUAL OUTCOME
        # -------------------------------------------------
        # IMPORTANT:
        # actual_recovered is accessed ONLY AFTER the
        # agent has already made its decision.
        #
        # This is valid for offline evaluation.
        # -------------------------------------------------

        actual_recovered = bool(
            row["actual_recovered"]
        )

        success = False
        recovered_amount = 0.0

        # -------------------------------------------------
        # RETRY
        # -------------------------------------------------

        if action == "retry":

            retry_actions += 1
            recovery_attempts += 1

            if actual_recovered:

                success = True
                successful_recoveries += 1

                recovered_amount = transaction.amount
                revenue_recovered += transaction.amount

        # -------------------------------------------------
        # CUSTOMER NOTIFICATION
        # -------------------------------------------------

        elif action == "notify_customer":

            customer_notifications += 1

        # -------------------------------------------------
        # MERCHANT APPROVAL
        # -------------------------------------------------

        elif action == "request_approval":

            merchant_escalations += 1

            # Detect high-value transactions requiring approval
            if transaction.amount > 5000:
                high_value_escalations += 1

        # -------------------------------------------------
        # STOP / ESCALATE
        # -------------------------------------------------

        elif action in ["stop", "escalate"]:

            blocked_actions += 1

            # -------------------------------------------------
            # SAFETY REASON ANALYSIS
            # -------------------------------------------------

            reason = decision.get("reason", "").lower()

            if "risk score" in reason:
                high_risk_blocked += 1

            if "retry count" in reason:
                retry_limit_blocked += 1

        # -------------------------------------------------
        # STORE TRANSACTION RESULT
        # -------------------------------------------------

        results.append({
            "transaction_id": transaction.transaction_id,
            "amount": transaction.amount,
            "failure_reason": transaction.failure_reason,
            "payment_method": transaction.payment_method,
            "bank": transaction.bank,
            "retry_count": transaction.retry_count,
            "risk_score": transaction.risk_score,

            "recovery_probability": recovery_probability,
            "expected_recovery_value": expected_recovery_value,

            "recoverable": recoverable,
            "automatically_actionable": automatically_actionable,

            "action": action,
            "decision_reason": decision.get(
                "reason",
                ""
            ),

            # Used ONLY for offline evaluation
            "actual_recovered": actual_recovered,

            "successful_recovery": success,
            "recovered_amount": recovered_amount,
        })

    # ---------------------------------------------------------
    # CALCULATE METRICS
    # ---------------------------------------------------------

    recovery_success_rate = (
        successful_recoveries / recovery_attempts
        if recovery_attempts > 0
        else 0.0
    )

    # Revenue recovered relative to ALL failed revenue
    gross_revenue_recovery_rate = (
        revenue_recovered / total_failed_revenue
        if total_failed_revenue > 0
        else 0.0
    )

    # Revenue recovered relative to potentially recoverable
    recoverable_revenue_rate = (
        revenue_recovered / potentially_recoverable_revenue
        if potentially_recoverable_revenue > 0
        else 0.0
    )

    # Revenue recovered relative to automatically actionable revenue
    automatic_recovery_rate = (
        revenue_recovered / automatically_actionable_revenue
        if automatically_actionable_revenue > 0
        else 0.0
    )

    # Average recovered amount per successful recovery
    average_recovered_amount = (
        revenue_recovered / successful_recoveries
        if successful_recoveries > 0
        else 0.0
    )

    # Average expected value of automatic retry decisions
    average_expected_value = (
        sum(
            r["expected_recovery_value"]
            for r in results
            if r["action"] == "retry"
        )
        / recovery_attempts
        if recovery_attempts > 0
        else 0.0
    )

    # ---------------------------------------------------------
    # ACTION DISTRIBUTION
    # ---------------------------------------------------------

    action_counts = (
        pd.DataFrame(results)["action"]
        .value_counts()
        .to_dict()
    )

    # ---------------------------------------------------------
    # SAVE DETAILED RESULTS
    # ---------------------------------------------------------

    results_df = pd.DataFrame(results)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    results_df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    # ---------------------------------------------------------
    # PRINT FINAL REPORT
    # ---------------------------------------------------------

    print()
    print("=" * 72)
    print("                    RECOVERR BATCH EVALUATION")
    print("=" * 72)

    print()
    print("DATASET")
    print("-" * 72)

    print(
        f"Test transactions evaluated : "
        f"{total_transactions:,}"
    )

    print(
        f"Total failed revenue         : "
        f"₹{total_failed_revenue:,.2f}"
    )

    print(
        f"Potentially recoverable      : "
        f"₹{potentially_recoverable_revenue:,.2f}"
    )

    print(
        f"Automatically actionable     : "
        f"₹{automatically_actionable_revenue:,.2f}"
    )

    print()
    print("RECOVERY PERFORMANCE")
    print("-" * 72)

    print(
        f"Recovery attempts            : "
        f"{recovery_attempts:,}"
    )

    print(
        f"Successful recoveries        : "
        f"{successful_recoveries:,}"
    )

    print(
        f"Recovery success rate        : "
        f"{recovery_success_rate * 100:.2f}%"
    )

    print(
        f"Revenue recovered            : "
        f"₹{revenue_recovered:,.2f}"
    )

    print(
        f"Recovery of failed revenue   : "
        f"{gross_revenue_recovery_rate * 100:.2f}%"
    )

    print(
        f"Recovery of recoverable      : "
        f"{recoverable_revenue_rate * 100:.2f}%"
    )

    print(
        f"Automatic recovery rate      : "
        f"{automatic_recovery_rate * 100:.2f}%"
    )

    print(
        f"Avg recovered / success      : "
        f"₹{average_recovered_amount:,.2f}"
    )

    print(
        f"Avg expected value / retry   : "
        f"₹{average_expected_value:,.2f}"
    )

    print()
    print("AGENT ACTIONS")
    print("-" * 72)

    print(
        f"Automatic retries            : "
        f"{retry_actions:,}"
    )

    print(
        f"Customer notifications       : "
        f"{customer_notifications:,}"
    )

    print(
        f"Merchant escalations         : "
        f"{merchant_escalations:,}"
    )

    print(
        f"Blocked / stopped            : "
        f"{blocked_actions:,}"
    )

    print()
    print("SAFETY / GUARDRAILS")
    print("-" * 72)

    print(
        f"High-risk actions blocked    : "
        f"{high_risk_blocked:,}"
    )

    print(
        f"Retry-limit blocks           : "
        f"{retry_limit_blocked:,}"
    )

    print(
        f"High-value escalations       : "
        f"{high_value_escalations:,}"
    )

    print()
    print("ACTION DISTRIBUTION")
    print("-" * 72)

    for action, count in sorted(
        action_counts.items(),
        key=lambda x: x[1],
        reverse=True
    ):
        percentage = (
            count / total_transactions * 100
            if total_transactions > 0
            else 0
        )

        print(
            f"{action:<28} "
            f"{count:>6,} "
            f"({percentage:>6.2f}%)"
        )

    print()
    print("=" * 72)

    print()
    print("Detailed results saved to:")
    print(OUTPUT_PATH)

    print()
    print("Evaluation integrity:")
    print(
        "✓ Agent decisions made without actual_recovered"
    )
    print(
        "✓ actual_recovered used only after decision"
    )
    print(
        "✓ Evaluation performed on held-out test set"
    )
    print(
        "✓ Recovery threshold selected before final test evaluation"
    )

    print()


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------

if __name__ == "__main__":
    run_batch()