import streamlit as st
import requests
import time


# =========================================================
# CONFIG
# =========================================================

API_URL = "http://127.0.0.1:8000/recover"


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="RecoverR",
    page_icon="₹",
    layout="wide"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .main {
        padding-top: 1rem;
    }

    .hero {
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid #333;
        margin-bottom: 1.5rem;
    }

    .hero-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .hero-subtitle {
        font-size: 18px;
        opacity: 0.75;
    }

    .metric-card {
        padding: 20px;
        border-radius: 14px;
        border: 1px solid #333;
        text-align: center;
        min-height: 120px;
    }

    .metric-value {
        font-size: 30px;
        font-weight: 750;
    }

    .metric-label {
        opacity: 0.65;
        font-size: 14px;
    }

    .step {
        padding: 14px;
        border-radius: 12px;
        border: 1px solid #333;
        text-align: center;
        margin-bottom: 10px;
    }

    .success-box {
        padding: 20px;
        border-radius: 14px;
        border: 2px solid #2ecc71;
        text-align: center;
        margin-top: 15px;
    }

    .danger-box {
        padding: 20px;
        border-radius: 14px;
        border: 2px solid #e74c3c;
        text-align: center;
        margin-top: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">RecoverR</div>
        <div class="hero-subtitle">
            Autonomous Revenue Recovery Agent
        </div>
        <br>
        <div>
            Detect → Diagnose → Predict → Decide → Guardrail
            → Execute → Verify → Audit
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# DASHBOARD METRICS
# =========================================================

st.subheader("Revenue Recovery Overview")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-value">₹37.07L</div>
            <div class="metric-label">Revenue at Risk</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-value">₹4.24L</div>
            <div class="metric-label">Revenue Recovered</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c3:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-value">60.67%</div>
            <div class="metric-label">Recovery Success</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c4:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-value">389</div>
            <div class="metric-label">Automatic Retries</div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.write("")


# =========================================================
# SECONDARY METRICS
# =========================================================

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "Customer Notifications",
        "281"
    )

with c2:
    st.metric(
        "Merchant Escalations",
        "41"
    )

with c3:
    st.metric(
        "Blocked / Stopped",
        "789"
    )


st.divider()


# =========================================================
# LIVE RECOVERY DEMO
# =========================================================

st.header("Live Agent Demo")

st.write(
    "Submit a failed payment and watch RecoverR decide "
    "whether and how it should attempt recovery."
)


left, right = st.columns(2)


with left:

    st.subheader("Failed Payment")

    transaction_id = st.text_input(
        "Transaction ID",
        value="demo_txn_001"
    )

    amount = st.number_input(
        "Amount (₹)",
        min_value=1.0,
        value=2499.0,
        step=100.0
    )

    payment_method = st.selectbox(
        "Payment Method",
        [
            "card",
            "upi",
            "netbanking",
            "wallet"
        ]
    )

    bank = st.selectbox(
        "Bank",
        [
            "HDFC",
            "ICICI",
            "SBI",
            "AXIS",
            "KOTAK"
        ]
    )

    failure_reason = st.selectbox(
        "Failure Reason",
        [
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
    )

    retry_count = st.number_input(
        "Previous Retry Count",
        min_value=0,
        max_value=10,
        value=0
    )

    previous_transactions = st.number_input(
        "Previous Transactions",
        min_value=0,
        value=10
    )

    previous_successful_transactions = st.number_input(
        "Previous Successful Transactions",
        min_value=0,
        value=9
    )

    risk_score = st.slider(
        "Risk Score",
        min_value=0.0,
        max_value=1.0,
        value=0.12,
        step=0.01
    )


    recover_button = st.button(
        "🚀 Run RecoverR Agent",
        type="primary",
        use_container_width=True
    )


# =========================================================
# AGENT EXECUTION
# =========================================================

with right:

    st.subheader("Agent Execution")

    if recover_button:

        payload = {
            "transaction_id": transaction_id,
            "customer_id": "demo_customer_001",
            "amount": amount,
            "payment_method": payment_method,
            "bank": bank,
            "status": "failed",
            "failure_reason": failure_reason,
            "retry_count": retry_count,
            "previous_transactions": previous_transactions,
            "previous_successful_transactions":
                previous_successful_transactions,
            "risk_score": risk_score
        }

        try:

            with st.spinner(
                "RecoverR is analyzing the payment..."
            ):

                response = requests.post(
                    API_URL,
                    json=payload,
                    timeout=30
                )

            if response.status_code != 200:

                st.error(
                    f"API Error: {response.status_code}"
                )

            else:

                data = response.json()

                decision = data["decision"]
                execution = data["execution"]

                # -------------------------------------------------
                # AGENT PIPELINE
                # -------------------------------------------------

                st.markdown("### Agent Pipeline")

                steps = [
                    "👁️ Observe",
                    "🔍 Diagnose",
                    "🧠 Predict",
                    "⚖️ Decide",
                    "🛡️ Guardrail",
                    "⚡ Execute",
                    "✅ Verify",
                    "📝 Audit"
                ]

                for step in steps:

                    st.markdown(
                        f"""
                        <div class="step">
                            {step}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                # -------------------------------------------------
                # DECISION
                # -------------------------------------------------

                st.markdown("### Decision")

                probability = decision.get(
                    "recovery_probability",
                    0
                )

                expected_value = decision.get(
                    "expected_recovery_value",
                    0
                )

                action = decision.get(
                    "action",
                    "unknown"
                )

                st.metric(
                    "Recovery Probability",
                    f"{probability * 100:.1f}%"
                )

                st.metric(
                    "Expected Recovery Value",
                    f"₹{expected_value:,.2f}"
                )

                st.info(
                    f"**Selected Action:** `{action}`\n\n"
                    f"{decision.get('reason', '')}"
                )

                # -------------------------------------------------
                # EXECUTION RESULT
                # -------------------------------------------------

                st.markdown("### Execution")

                execution_status = execution.get(
                    "execution_status",
                    "unknown"
                )

                verification_status = execution.get(
                    "verification_status",
                    "unknown"
                )

                if verification_status == "verified":

                    recovered_amount = execution.get(
                        "recovered_amount",
                        0
                    )

                    st.markdown(
                        f"""
                        <div class="success-box">
                            <h2>₹{recovered_amount:,.2f} RECOVERED</h2>
                            <p>Payment successfully verified.</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                elif execution_status == "blocked":

                    st.markdown(
                        """
                        <div class="danger-box">
                            <h3>Recovery Stopped</h3>
                            <p>
                            RecoverR blocked the action
                            according to policy.
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                else:

                    st.warning(
                        f"Execution: {execution_status}\n\n"
                        f"Verification: {verification_status}"
                    )

                # -------------------------------------------------
                # RAW RESULT
                # -------------------------------------------------

                with st.expander(
                    "View complete agent response"
                ):

                    st.json(data)

        except requests.exceptions.ConnectionError:

            st.error(
                "Cannot connect to RecoverR API. "
                "Make sure Uvicorn is running on "
                "http://127.0.0.1:8000"
            )

        except Exception as e:

            st.error(
                f"Unexpected error: {e}"
            )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "RecoverR — Autonomous Revenue Recovery Agent | "
    "Buildathon Prototype | Test/Synthetic Environment"
)