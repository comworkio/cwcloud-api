from utils.common import is_empty
from utils.mail import send_contact_email
from utils.security import is_not_email_valid
import os
from fastapi import APIRouter
from schemas.Contact import ContactSchema
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("")
def contact_with_us(payload: ContactSchema):
    email = payload.email
    subject = payload.subject
    message = payload.message
    if is_empty(email) or is_empty(subject) or is_empty(message):
        return JSONResponse(content = {"error": "missing informations", "i18n_code": "1207"}, status_code = 400)

    if is_not_email_valid(email):
        return JSONResponse(content = {"error": "Invalid email", "i18n_code": "1206"}, status_code = 400)

    receiver_contact_mails = os.environ["RECEIVER_CONTACTS_EMAIL"]
    send_contact_email(email, receiver_contact_mails, message, subject)
    return JSONResponse(content = {"message": "successfully sent contact email"}, status_code = 200)
