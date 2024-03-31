import os
import base64
import json

from fastapi import Depends, APIRouter, Query
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from urllib.error import HTTPError
from typing import Annotated
from sqlalchemy.orm import Session

from database.postgres_db import get_db
from entities.Invoice import Invoice
from schemas.User import UserSchema
from schemas.Invoice import InvoiceSchema, InvoiceUpdateSchema, InvoiceDownloadSchema, InvoiceEditionSchema
from middleware.auth_guard import admin_required

from utils.encoder import AlchemyEncoder
from utils.common import is_false, is_not_empty
from utils.file import quiet_remove
from utils.flag import is_flag_disabled, is_flag_enabled
from utils.security import is_not_ref_invoice_valid
from utils.user import pick_user_id_if_exists, user_from_body, user_id_from_body
from utils.consumption import generate_user_consumptions
from utils.invoice import add_subscription, get_invoice_ref
from utils.logger import log_msg
from utils.mail import send_invoice_email
from utils.invoice import generate_invoice_pdf
from utils.consumption import getUserConsumptionsByDate
from utils.date import parse_date
from utils.payment import get_min_amount
from utils.billing import download_billing_file
from utils.observability.cid import get_current_cid
from utils.observability.otel import get_otel_tracer
from utils.observability.traces import span_format
from utils.observability.counter import create_counter, increment_counter
from utils.observability.enums import Action, Method

router = APIRouter()

_span_prefix = "adm-invoice"
_counter = create_counter("adm_invoice_api", "Admin invoice API counter")

@router.post("/generate")
def generate_invoice(current_user: Annotated[UserSchema, Depends(admin_required)], payload: InvoiceSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.POST)):
        increment_counter(_counter, Method.POST)
        from_date = parse_date(payload.from_)
        to_date = parse_date(payload.to)
        email = payload.email
        send = payload.send
        preview = payload.preview

        from_date_iso = from_date["value"]
        if is_false(from_date["status"]):
            return JSONResponse(content = {
                'status': 'ko',
                'error': "The date is not correct: {}".format(from_date_iso),
                'i18n_code': 'bad_date_aaaammdd',
                'cid': get_current_cid()
            }, status_code = 400)

        to_date_iso = to_date["value"]
        if is_false(to_date["status"]):
            return JSONResponse(content = {
                'status': 'ko',
                'error': "The date is not correct: {}".format(to_date_iso),
                'i18n_code': 'bad_date_aaaammdd',
                'cid': get_current_cid()
            }, status_code = 400)

        from entities.User import User
        target_user = User.getUserByEmail(email, db)
        if not target_user:
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'user not found',
                'i18n_code': '304',
                'cid': get_current_cid()
            }, status_code = 404)

        if is_flag_disabled(target_user.enabled_features, 'billable'):
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'user not billable',
                'i18n_code': 'not_billable',
                'cid': get_current_cid()
            }, status_code = 400)

        consumptions = getUserConsumptionsByDate(from_date, to_date, target_user.id, db)
        all_consumptions = generate_user_consumptions(target_user.id, from_date_iso, to_date_iso, db)
        all_consumptions.extend(consumptions)
        consumptions_dict = []
        subscriptions = []
        total_ht = 0
        for row in all_consumptions:
            consumption = {
                "instance_type": row["instance"]["type"],
                "from_date": datetime.fromisoformat(str(row["from_date"])).strftime("%Y/%m/%d, %H:%M:%S"),
                "to_date": datetime.fromisoformat(str(row["to_date"])).strftime("%Y/%m/%d, %H:%M:%S"),
                "usage": row["usage"],
                "instance_name": row["instance"]["name"],
                "instance_price": row["instance_price"],
                "total_price": row["total_price"]
            }

            total_ht = total_ht + row["total_price"]
            consumptions_dict.append(consumption)

        total_ht = total_ht + add_subscription(is_flag_enabled(target_user.enabled_features, 'emailapi'), "API_PRICE_EMAIL", "Email API", subscriptions) + add_subscription(is_flag_enabled(target_user.enabled_features, 'cwaiapi'), "API_PRICE_CWAI", "Cwai API", subscriptions)

        total_ttc = 0
        timbre_fiscal = os.getenv("TIMBRE_FISCAL")
        if is_flag_enabled(target_user.enabled_features, 'without_vat'):
            total_ttc = round(total_ht, 4)
        elif is_not_empty(timbre_fiscal):
            total_ttc = round((total_ht * float(os.getenv("TTVA"))) + float(timbre_fiscal), 4)
        else:
            total_ttc = round(total_ht * float(os.getenv("TTVA")), 4)

        total_ht = round(total_ht, 4)

        invoice_ref = get_invoice_ref(db)
        new_invoice = Invoice()
        new_invoice.ref = invoice_ref
        new_invoice.from_date = from_date_iso
        new_invoice.to_date = to_date_iso
        new_invoice.user_id = target_user.id
        new_invoice.total_price = total_ttc

        name_file = generate_invoice_pdf(invoice_ref, target_user, consumptions_dict, subscriptions, from_date_iso, to_date_iso, total_ht, total_ttc, is_flag_enabled(target_user.enabled_features, 'without_vat'))
        min_amount = get_min_amount()

        new_invoice.details = {
            "consumptions": consumptions_dict,
            "subscriptions": subscriptions,
            "total_ht": total_ht,
            "total_ttc": total_ttc
        }

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

                log_msg("INFO", f"[api_invoice] Created new invoice between {from_date_iso} and {to_date_iso} for user {target_user.email}")

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

@router.post("/edition")
def invoice_edition(current_user: Annotated[UserSchema, Depends(admin_required)], payload: InvoiceEditionSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.POST, Action.EDIT)):
        increment_counter(_counter, Method.POST, Action.EDIT)
        from entities.Invoice import Inoice
        user = user_from_body(payload)
        search_user_id = pick_user_id_if_exists(user)
        if is_false(search_user_id['status']):
            return JSONResponse(content = {
                'status': 'ko',
                'error': search_user_id['message'],
                'i18n_code': search_user_id['i18n_code'],
                'cid': get_current_cid()
            }, status_code = search_user_id['http_code'])

        invoice_ref = payload.ref
        if is_not_ref_invoice_valid(invoice_ref):
            return JSONResponse(content = {
                'status': 'ko',
                'error': "The reference is not correct: ref = {}".format(invoice_ref),
                'i18n_code': 'bad_invoice_ref',
                'cid': get_current_cid()
            }, status_code = 400)

        invoice = Invoice.getInvoiceByRefAndUser(invoice_ref, search_user_id["id"], db)
        if is_false(invoice):
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'invoice not found',
                'i18n_code': '604',
                'cid': get_current_cid()
            }, status_code = 404)

        new_ref = payload.new_ref
        if is_not_ref_invoice_valid(new_ref):
            return JSONResponse(content = {
                'status': 'ko',
                'error': "The reference is not correct: new_ref = {}".format(new_ref),
                'i18n_code': 'bad_invoice_ref',
                'cid': get_current_cid()
            }, status_code = 400)

        details = invoice.details
        consumptions = []
        subscriptions = []
        total_ht = invoice.total_price if is_flag_disabled(user.enabled_features, 'without_vat') else invoice.total_price - ((1 - float(os.getenv("TTVA"))) * invoice.total_price)
        total_ttc = invoice.total_price
        if is_not_empty(details) and "consumptions" in details and is_not_empty(details["consumptions"]):
            consumptions = details["consumptions"]

        if is_not_empty(details) and "subscriptions" in details and is_not_empty(details["subscriptions"]):
            subscriptions = details["subscriptions"]

        if is_not_empty(details) and "total_ht" in details and is_not_empty(details["total_ht"]):
            total_ht = float(details["total_ht"])

        if is_not_empty(details) and "total_ttc" in details and is_not_empty(details["total_ttc"]):
            total_ttc = float(details["total_ttc"])

        Invoice.updateInvoiceRef(invoice_ref, new_ref)
        name_file = generate_invoice_pdf(new_ref, user, consumptions, subscriptions, invoice.from_date, invoice.to_date, total_ht, total_ttc, is_flag_enabled(user.enabled_features, 'without_vat'))
        min_amount = get_min_amount()
        updated_invoice = Invoice.getInvoiceByRefAndUser(new_ref, search_user_id["id"], db)

        updated_invoice.details = {
            "consumptions": consumptions,
            "subscriptions": subscriptions,
            "total_ht": total_ht,
            "total_ttc": total_ttc
        }

    try:
        encoded_string = ""
        with open(name_file, "rb") as pdf_file:
            encoded_string = base64.b64encode(pdf_file.read()).decode()
        pdf_file.close()
        if total_ttc <= min_amount:
            updated_invoice.status = "paid"

        updated_invoice.save(db)

        if total_ttc > min_amount and is_flag_disabled(user.enabled_features, 'disable_emails'):
            date_path = (invoice.to_date + timedelta(days = int(os.environ["INVOICE_DAYS_DELTA"]))).strftime("%Y-%m")
            log_msg("DEBUG", "[InvoiceAdminUpdate][post] edition, date_path = {}".format(date_path))
            send_invoice_email(user.email, name_file, encoded_string, True, True, date_path)
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
        'message': 'Invoice successfully updated',
        'i18n_code': '301'
    }, status_code = 200)

@router.post("/{invoice_ref}/download")
def download_invoice(current_user: Annotated[UserSchema, Depends(admin_required)], invoice_ref: str, payload: InvoiceDownloadSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.POST, Action.DOWNLOAD)):
        increment_counter(_counter, Method.POST, Action.DOWNLOAD)
        search_user_id = user_id_from_body(payload, db)
        if is_false(search_user_id['status']):
            return JSONResponse(content = {
                'status': 'ko',
                'error': search_user_id['message'],
                'i18n_code': search_user_id['i18n_code'],
                'cid': get_current_cid()
            }, status_code = search_user_id['http_code'])

        user_invoice = Invoice.getInvoiceByRefAndUser(invoice_ref, search_user_id["id"], db)
        if is_false(user_invoice):
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'invoice not found',
                'i18n_code': '604',
                'cid': get_current_cid()
            }, status_code = 404)

        target_name, download_status = download_billing_file("invoice", search_user_id["id"], user_invoice)
        if is_false(download_status["status"]):
            return JSONResponse(content = {
                'status': 'ko',
                'error': download_status['message'],
                'i18n_code': download_status['i18n_code'],
                'cid': get_current_cid()
            }, status_code = download_status['http_code'])

        encoded_string = ""
        with open(target_name, "rb") as pdf_file:
            encoded_string = base64.b64encode(pdf_file.read()).decode()

        pdf_file.close()
        quiet_remove(target_name)
        return JSONResponse(content = {
            'status': 'ok',
            'file_name': target_name,
            'blob': str(encoded_string)
        }, status_code = 200)

@router.get("/{user_email}")
def get_invoice_by_user_email(current_user: Annotated[UserSchema, Depends(admin_required)], user_email: str, from_date: str = Query(None, alias = "from"), to_date: str = Query(None, alias = "to"), db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.BYEMAIL)):
        increment_counter(_counter, Method.GET, Action.BYEMAIL)
        from entities.User import User
        target_user = User.getUserByEmail(user_email, db)
        if not target_user:
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'user not found',
                'i18n_code': '304',
                'cid': get_current_cid()
            }, status_code = 404)

        invoices = []
        if to_date and from_date:
            invoices = Invoice.getUserInvoicesByDate(target_user.id, from_date, to_date, db)
        else:
            invoices = Invoice.getUserAllInvoices(target_user.id, db)

        invoices_json = []
        for invoice in invoices:
            dumpedInvoice = json.loads(json.dumps(invoice, cls = AlchemyEncoder))
            invoices_json.append({**dumpedInvoice, "date_created": str(invoice.date_created), "from_date": str(invoice.from_date), "to_date": str(invoice.to_date)})
        return JSONResponse(content = invoices_json, status_code = 200)

@router.get("/{invoice_id}")
def get_invoice_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], invoice_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET)):
        increment_counter(_counter, Method.GET)
        user_invoice = Invoice.getInvoiceById(invoice_id, db)
        if is_false(user_invoice):
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'invoice not found',
                'i18n_code': '604',
                'cid': get_current_cid()
            }, status_code = 404)

        dumpedInvoice = json.loads(json.dumps(user_invoice, cls = AlchemyEncoder))
        invoiceJson = {**dumpedInvoice, "date_created": str(user_invoice.date_created), "from_date": str(user_invoice.from_date), "to_date": str(user_invoice.to_date)}
        return JSONResponse(content = invoiceJson, status_code = 200)

@router.patch("/{invoice_id}")
def update_invoice_status(current_user: Annotated[UserSchema, Depends(admin_required)], invoice_id: str, payload: InvoiceUpdateSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix)):
        increment_counter(_counter, Method.PATCH)
        status = payload.status
        user_invoice = Invoice.getInvoiceById(invoice_id, db)
        if is_false(user_invoice):
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'invoice not found',
                'i18n_code': '604',
                'cid': get_current_cid()
            }, status_code = 404)

        if status not in ["paid", "unpaid", "canceled"]:
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'invalid invoice status',
                'cid': get_current_cid()
            }, status_code = 400)

        Invoice.updateInvoiceStatus(invoice_id, status, db)
        return JSONResponse(content = {
            'status': 'ok',
            'message': 'invoice successfully updated',
            'i18n_code': '601'
        }, status_code = 200)
