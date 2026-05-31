from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid
from models import QRRequest, LoginRequest, CheckRequest
from qr_generator import generate_upi_qr
from database import save_order, get_gmail, save_gmail
from gmail import check_payment

app = FastAPI(title="FamPay Auto API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate-qr")
async def generate_qr(data: QRRequest):
    result = generate_upi_qr(data.upi_id, data.amount, data.note)
    save_order(result["order_id"], data.upi_id, data.amount, data.note)
    return result

@app.post("/login-gmail")
async def login_gmail(data: LoginRequest):
    # Simple unique api key generate karo
    api_key = "fampay_" + str(uuid.uuid4().hex[:16])
    save_gmail(api_key, data.email, data.app_password)
    return {
        "success": True,
        "api_key": api_key,
        "message": "Gmail Connected Successfully"
    }

@app.post("/check-payment")
async def check_payment_status(data: CheckRequest):
    creds = get_gmail(data.api_key)
    if not creds:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    
    result = check_payment(creds[0], creds[1], data.order_id)
    return result

@app.get("/")
def home():
    return {"message": "FamPay Auto API is Running ✅"}
