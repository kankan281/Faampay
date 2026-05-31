import imaplib
import email
from email.header import decode_header
from bs4 import BeautifulSoup
import re

def check_payment(email_id: str, app_password: str, order_id: str):
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(email_id, app_password)
        mail.select("inbox")

        _, messages = mail.search(None, 'FROM "fampay" OR FROM "no-reply@fampay.in"')
        
        for num in messages[0].split()[-15:]:  # last 15 emails
            _, msg = mail.fetch(num, "(RFC822)")
            email_body = msg[0][1]
            email_message = email.message_from_bytes(email_body)

            subject = decode_header(email_message["Subject"])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()

            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/html":
                        html = part.get_payload(decode=True).decode()
                        soup = BeautifulSoup(html, "lxml")
                        text = soup.get_text()

                        if order_id in text or order_id.lower() in text.lower():
                            # Extract details using regex
                            utr = re.search(r'UTR[:\s]+(\d+)', text)
                            payer = re.search(r'from[:\s]+([A-Za-z0-9.@]+)', text, re.I)
                            amount_match = re.search(r'₹?(\d+\.?\d*)', text)

                            return {
                                "status": "success",
                                "order_id": order_id,
                                "utr": utr.group(1) if utr else None,
                                "amount": amount_match.group(1) if amount_match else None,
                                "payer_vpa": payer.group(1) if payer else None,
                                "message": "Payment Received"
                            }
        mail.logout()
        return {"status": "pending", "message": "Payment not found yet"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
