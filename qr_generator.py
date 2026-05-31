import qrcode
import uuid
from io import BytesIO
import base64

def generate_upi_qr(upi_id: str, amount: float, note: str = "Payment"):
    order_id = "ORD" + str(uuid.uuid4().hex[:12]).upper()
    
    upi_string = f"upi://pay?pa={upi_id}&am={amount}&cu=INR&tn={note}&tr={order_id}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(upi_string)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    return {
        "order_id": order_id,
        "upi_string": upi_string,
        "qr_base64": qr_base64,
        "qr_url": f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={upi_string}"
    }
