import json
import base64

from typing import Annotated
from fastapi import Depends, APIRouter, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database.postgres_db import get_db
from middleware.auth_guard import get_current_active_user
from schemas.User import UserSchema

from utils.billing import download_billing_file
from utils.common import is_false
from utils.encoder import AlchemyEncoder
from utils.file import quiet_remove
from utils.logger import log_msg
from utils.observability.otel import get_otel_tracer
from utils.observability.traces import span_format
from utils.observability.counter import create_counter, increment_counter
from utils.observability.enums import Action, Method
from utils.observability.cid import get_current_cid

router = APIRouter()

_span_prefix = "invoice"
_counter = create_counter("invoice_api", "Invoice API counter")

@router.get("/{invoice_ref}/download")
def download_invoice_by_invoice_ref(current_user: Annotated[UserSchema, Depends(get_current_active_user)], invoice_ref: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.DOWNLOAD)):
        increment_counter(_counter, Method.GET, Action.DOWNLOAD)
        from entities.Invoice import Invoice
        user_invoice = Invoice.getInvoiceByRefAndUser(invoice_ref, current_user.id, db)
        if is_false(user_invoice):
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'invoice not found', 
                'i18n_code': 'invoice_not_found',
                'cid': get_current_cid()
            }, status_code = 404)

        target_name, download_status = download_billing_file("invoice", current_user.id, user_invoice)
        if is_false(download_status["status"]):
            return JSONResponse(content = {
                'status': 'ko',
                'error': download_status['message'], 
                'i18n_code': download_status['i18n_code'],
                'cid': get_current_cid()
            }, status_code = download_status["http_code"])

        encoded_string = ""
        with open(target_name, "rb") as pdf_file:
            log_msg("INFO", f"[download_invoice_by_invoice_ref] writing file {target_name} content in response")
            encoded_string = base64.b64encode(pdf_file.read()).decode()
            pdf_file.close()
    
        log_msg("INFO", f"[download_invoice_by_invoice_ref] trying to delete {target_name}")
        quiet_remove(target_name)
        return JSONResponse(content = {"file_name": target_name, "blob": str(encoded_string)}, status_code = 200)

@router.get("")
def get_invoice(current_user: Annotated[UserSchema, Depends(get_current_active_user)], from_date: str = Query(None, alias = "from"), to_date: str = Query(None, alias = "to"), db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET)):
        increment_counter(_counter, Method.GET)
        from entities.Invoice import Invoice
        invoices = []
        if to_date and from_date:
            invoices = Invoice.getUserInvoicesByDate(current_user.id, from_date, to_date, db)
        else:
            invoices = Invoice.getUserAllInvoices(current_user.id, db)

        invoices_json = []
        for invoice in invoices:
            dumpedInvoice = json.loads(json.dumps(invoice, cls = AlchemyEncoder))
            invoices_json.append({**dumpedInvoice, "date_created": str(invoice.date_created), "from_date": str(invoice.from_date), "to_date": str(invoice.to_date)})
        return JSONResponse(content = invoices_json, status_code = 200)

@router.get("/{invoice_ref}")
def get_invoice_by_ref(current_user: Annotated[UserSchema, Depends(get_current_active_user)], invoice_ref: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.BYURL)):
        increment_counter(_counter, Method.GET, Action.BYURL)
        from entities.Invoice import Invoice
        user_invoice = Invoice.getInvoiceByRefAndUser(invoice_ref, current_user.id, db)
        if is_false(user_invoice):
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'invoice not found', 
                'i18n_code': 'invoice_not_found',
                'cid': get_current_cid()
            }, status_code = 404)

        dumpedInvoice = json.loads(json.dumps(user_invoice, cls = AlchemyEncoder))
        invoiceJson = {**dumpedInvoice, "date_created": str(user_invoice.date_created), "from_date": str(user_invoice.from_date), "to_date": str(user_invoice.to_date)}
        return JSONResponse(content = invoiceJson, status_code = 200)
