"""
Mock Razorpay API
Simulates UPI payment processing
"""

import uuid
import random
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/mock/razorpay", tags=["Mock - Razorpay"])


class PaymentRequest(BaseModel):
    amount: float
    upi_id: str
    description: Optional[str] = None
    worker_id: Optional[str] = None


@router.post("/pay")
async def process_payment(request: PaymentRequest):
    """Simulate UPI payment processing."""
    # Simulate payment (95% success rate)
    is_success = random.random() < 0.95
    txn_id = f"UPI_{uuid.uuid4().hex[:12].upper()}"

    if is_success:
        return {
            "success": True,
            "transaction_id": txn_id,
            "amount": request.amount,
            "upi_id": request.upi_id,
            "status": "COMPLETED",
            "method": "UPI",
            "timestamp": "2026-04-01T11:00:00Z",
            "message": f"₹{request.amount:,.0f} sent to {request.upi_id}",
            "_source": "mock_razorpay",
        }

    return {
        "success": False,
        "transaction_id": txn_id,
        "amount": request.amount,
        "upi_id": request.upi_id,
        "status": "FAILED",
        "error": random.choice([
            "UPI timeout",
            "Insufficient balance",
            "Bank server error",
        ]),
        "_source": "mock_razorpay",
    }


@router.post("/collect")
async def collect_payment(request: PaymentRequest):
    """Simulate UPI collection (premium payment)."""
    txn_id = f"COL_{uuid.uuid4().hex[:12].upper()}"

    return {
        "success": True,
        "transaction_id": txn_id,
        "amount": request.amount,
        "upi_id": request.upi_id,
        "status": "COLLECTED",
        "method": "UPI_COLLECT",
        "message": f"₹{request.amount:,.0f} collected from {request.upi_id}",
        "_source": "mock_razorpay",
    }


@router.get("/status/{transaction_id}")
async def get_payment_status(transaction_id: str):
    """Check payment status."""
    return {
        "transaction_id": transaction_id,
        "status": "COMPLETED",
        "method": "UPI",
        "_source": "mock_razorpay",
    }
