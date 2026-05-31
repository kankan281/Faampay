from pydantic import BaseModel
from typing import Optional

class QRRequest(BaseModel):
    upi_id: str
    amount: float
    note: Optional[str] = "Payment"

class LoginRequest(BaseModel):
    email: str
    app_password: str

class CheckRequest(BaseModel):
    api_key: str
    order_id: str
