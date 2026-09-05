from pydantic import BaseModel
from typing import Optional


class Transaction(BaseModel):
    transaction_id: str
    customer_id: str
    amount: float
    payment_method: str
    bank: Optional[str] = None
    status: str
    failure_reason: Optional[str] = None
    retry_count: int = 0
    previous_transactions: int = 0
    previous_successful_transactions: int = 0
    risk_score: float = 0.0
    payment_recovered: bool = False


class RecoveryDecision(BaseModel):
    transaction_id: str
    recoverable: bool
    recovery_probability: float
    action: str
    reason: str
    requires_approval: bool = False