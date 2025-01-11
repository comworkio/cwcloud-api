import os
import base64

from urllib.error import HTTPError
from typing import Annotated

from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database.postgres_db import get_db
from entities.User import User
from schemas.User import UserSchema
from schemas.Invoice import InvoiceCustomSchema
from middleware.auth_guard import admin_required

from utils.billing import TIMBRE_FISCAL, TTVA
from utils.common import is_false, is_not_empty
from utils.file import quiet_remove
from utils.flag import is_flag_disabled, is_flag_enabled
from utils.date import parse_date
from utils.invoice import get_invoice_ref
from utils.logger import log_msg
from utils.mail import send_invoice_email
from utils.invoice import generate_invoice_pdf
from utils.payment import get_min_amount
from utils.observability.cid import get_current_cid
from utils.observability.otel import get_otel_tracer
from utils.observability.traces import span_format
from utils.observability.counter import create_counter, increment_counter
from utils.observability.enums import Action, Method

router = APIRouter()

_span_prefix = "adm-invoice-custom"
_counter = create_counter("adm_custom_invoice_api", "Admin custom invoice API counter")

@router.post("")
def create_custom_invoice(current_user: Annotated[UserSchema, Depends(admin_required)], payload: InvoiceCustomSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.POST)):
        increment_counter(_counter, Method.POST)
        email = payload.email
        send = payload.send
        preview = payload.preview
        items = payload.items
        fdate = parse_date(payload.date)
        invoice_date = fdate["value"]
        if is_false(fdate["status"]):
            return JSONResponse(content = {
                'status': 'ko',
                'error': "The date is not correct: {}".format(invoice_date),
                'i18n_code': 'bad_date_aaaammdd',
                'cid': get_current_cid()
            }, status_code = 400)

        target_user = User.getUserByEmail(email, db)
        if not target_user:
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'user not found',
                'i18n_code': 'user_not_found',
                'cid': get_current_cid()
            }, status_code = 404)

        if is_flag_disabled(target_user.enabled_features, 'billable'):
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'user not billable',
                'i18n_code': 'not_billable',
                'cid': get_current_cid()
            }, status_code = 400)

        items_dict = []
        total_ht = 0
        for item in items:
            try:
                itemd = {
                    "label": item.label,
                    "price": item.price
                }
            except AttributeError as ae:
                return JSONResponse(content = {
                    'status': 'ko',
                    'error': "not correct item: {}".format(ae),
                    'i18n_code': 'not_correct_item',
                    'cid': get_current_cid()
                }, status_code = 400)

            total_ht = total_ht + itemd["price"]
            items_dict.append(itemd)

        total_ttc = 0
        without_tva = is_flag_enabled(target_user.enabled_features, 'without_vat')
        if without_tva:
            total_ttc = round(total_ht, 4)
        elif is_not_empty(TIMBRE_FISCAL):
            total_ttc = round((total_ht * TTVA) + TIMBRE_FISCAL, 4)
        else:
            total_ttc = round(total_ht * TTVA, 4)

        total_ht = round(total_ht, 4)
        from entities.Invoice import Invoice

        invoice_ref = get_invoice_ref(db)
        new_invoice = Invoice()
        new_invoice.ref = invoice_ref
        new_invoice.from_date = invoice_date
        new_invoice.to_date = invoice_date
        new_invoice.user_id = target_user.id
        new_invoice.total_price = total_ttc
        name_file = generate_invoice_pdf(invoice_ref, target_user, [], items_dict, invoice_date, invoice_date, total_ht, total_ttc, without_tva)
        min_amount = get_min_amount()

        try:
            encoded_string = ""
            with open(name_file, "rb") as pdf_file:
                encoded_string = base64.b64encode(pdf_file.read()).decode()
                pdf_file.close()

            if is_false(preview):
                if total_ttc <= min_amount:
                    new_invoice.status = "paid"

                new_invoice.save(db)

                if total_ttc > min_amount and is_flag_disabled(target_user.enabled_features, 'disable_emails'):
                    send_invoice_email(email, name_file, encoded_string, send)

                log_msg("INFO", f"[api_invoice] Created new invoice for {invoice_date} for user {target_user.email}")

            quiet_remove(name_file)
        except HTTPError as e:
            return JSONResponse(content = {
                'status': 'ko',
                'error': e.msg,
                'i18n_code': e.headers['i18n_code'],
                'cid': get_current_cid()
            }, status_code = e.code)

        return JSONResponse(content = {
            'status': 'ok',
            'file_name': name_file,
            'blob': str(encoded_string)
        }, status_code = 200)
