from fastapi import FastAPI
from backend.models.schemas import Transaction
from backend.agents.decision import make_recovery_decision
from backend.services.recovery_service import execute_recovery


app = FastAPI(
    title="RecoverR",
    description="Autonomous Revenue Recovery Agent",
    version="1.0.0"
)


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "status": "running",
        "service": "RecoverR",
        "description": "Autonomous Revenue Recovery Agent"
    }


# ---------------------------------------------------------
# RECOVERY ENDPOINT
# ---------------------------------------------------------

@app.post("/recover")
def recover(transaction: Transaction):

    # -----------------------------------------------------
    # 1. OBSERVE + DIAGNOSE + PREDICT + DECIDE
    # -----------------------------------------------------

    decision = make_recovery_decision(transaction)

    # -----------------------------------------------------
    # 2. EXECUTE + VERIFY + AUDIT
    # -----------------------------------------------------

    execution = execute_recovery(
        transaction,
        decision
    )

    # -----------------------------------------------------
    # 3. FINAL AGENT RESPONSE
    # -----------------------------------------------------

    return {
        "agent": "RecoverR",

        "transaction": {
            "transaction_id": transaction.transaction_id,
            "amount": transaction.amount,
            "failure_reason": transaction.failure_reason
        },

        "decision": decision,

        "execution": execution,

        "agent_loop": [
            "observe",
            "diagnose",
            "predict",
            "decide",
            "guardrail",
            "execute",
            "verify",
            "audit"
        ]
    }