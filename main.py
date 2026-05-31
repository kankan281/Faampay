from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid
import os
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

@app.get("/")
def home():
    return {"message": "FamPay Auto API is Running ✅", "status": "live"}

@app.post("/generate-qr")
async def generate_qr(data: QRRequest):
    try:
        result = generate_upi_qr(data.upi_id, data.amount, data.note)
        save_order(result["order_id"], data.upi_id, data.amount, data.note)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login-gmail")
async def login_gmail(data: LoginRequest):
    try:
        api_key = "fampay_" + str(uuid.uuid4().hex[:16])
        save_gmail(api_key, data.email, data.app_password)
        return {
            "success": True,
            "api_key": api_key,
            "message": "Gmail Connected Successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check-payment")
async def check_payment_status(data: CheckRequest):
    creds = get_gmail(data.api_key)
    if not creds:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    
    result = check_payment(creds[0], creds[1], data.order_id)
    return result

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
