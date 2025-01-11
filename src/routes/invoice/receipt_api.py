import base64

from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse

from database.postgres_db import get_db
from schemas.User import UserSchema
from middleware.auth_guard import get_current_active_user

from utils.common import is_false
from utils.billing import download_billing_file
from utils.file import quiet_remove
from utils.observability.otel import get_otel_tracer
from utils.observability.traces import span_format
from utils.observability.counter import create_counter, increment_counter
from utils.observability.enums import Action, Method
from utils.observability.cid import get_current_cid

router = APIRouter()

_span_prefix = "receipt"
_counter = create_counter("receipt_api", "Receipt API counter")

@router.get("/{invoice_ref}/download")
def download_receipt_by_invoice_ref(current_user: Annotated[UserSchema, Depends(get_current_active_user)], invoice_ref: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.DOWNLOAD)):
        increment_counter(_counter, Method.GET, Action.DOWNLOAD)
        from entities.Invoice import Invoice
        user_invoice = Invoice.getInvoiceByRefAndUser(invoice_ref, current_user.id, db)
        if not user_invoice:
                return JSONResponse(content = {
                    'status': 'ko',
                    'error': 'invoice not found', 
                    'i18n_code': 'invoice_not_found',
                    'cid': get_current_cid()
                }, status_code = 404)

        target_name, download_status = download_billing_file("receipt", current_user.id, user_invoice)
        if is_false(download_status["status"]):
            return JSONResponse(content = {
                'status': 'ko',
                'error': download_status['message'], 
                'i18n_code': download_status['i18n_code'],
                'cid': get_current_cid()    
            }, status_code = download_status["http_code"])

        encoded_string = ""
        with open(target_name, "rb") as pdf_file:
            encoded_string = base64.b64encode(pdf_file.read()).decode()
            pdf_file.close()

        quiet_remove(target_name)
        return JSONResponse(content = {"file_name": target_name, "blob": str(encoded_string)}, status_code = 200)
