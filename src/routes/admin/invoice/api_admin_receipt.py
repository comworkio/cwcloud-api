
import os
import base64

from typing import Annotated
from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database.postgres_db import get_db
from schemas.User import UserSchema
from middleware.auth_guard import admin_required
from schemas.Receipt import ReceiptDownloadSchema

from utils.common import is_false
from utils.user import user_id_from_body
from utils.billing import download_billing_file

router = APIRouter()
@router.post("/{invoice_ref}/download")
def download_receipt(current_user: Annotated[UserSchema, Depends(admin_required)], invoice_ref: str, payload: ReceiptDownloadSchema, db: Session = Depends(get_db)):
    search_user_id = user_id_from_body(payload, db)
    if is_false(search_user_id["status"]):
        return JSONResponse(content = {"error": search_user_id["message"], "i18n_code": search_user_id["i18n_code"]}, status_code = search_user_id["http_code"])

    from entities.Invoice import Invoice
    user_invoice = Invoice.getInvoiceByRefAndUser(invoice_ref, search_user_id["id"], db)
    if not user_invoice:
        return JSONResponse(content = {"error": "invoice not found", "i18n_code": "604"}, status_code = 404)

    target_name, download_status = download_billing_file("receipt", search_user_id["id"], user_invoice)
    if is_false(download_status["status"]):
        return JSONResponse(content = {"error": download_status["message"], "i18n_code": download_status["i18n_code"]}, status_code = download_status["http_code"])

    encoded_string = ""
    with open(target_name, "rb") as pdf_file:
        encoded_string = base64.b64encode(pdf_file.read()).decode()

    pdf_file.close()
    os.remove(target_name)
    return JSONResponse(content = {"file_name": target_name, "blob": str(encoded_string)}, status_code = 200)
