import os
import base64
import datetime

from urllib.error import HTTPError
from fastapi.responses import JSONResponse

from adapters.AdapterConfig import get_adapter

from utils.file import quiet_remove
from utils.mail import send_relaunch_email
from utils.currency import get_payment_currency
from utils.invoice import generate_receipt_pdf
from utils.common import is_duration_valid, is_false, is_not_empty, is_numeric, is_true
from utils.logger import log_msg
from utils.observability.cid import get_current_cid

PAYMENT_ADAPTER = get_adapter("payments")

def get_min_amount():
    min = os.getenv('MIN_AMOUNT')
    return int(min) if is_numeric(min) else 0

def relaunch(user, invoice):
    total_to_pay = invoice.total_price

    if is_false(user['enabled_features']['billable']):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'user not billable', 
            'i18n_code': 'not_billable',
            'cid': get_current_cid()
        }, status_code = 400)

    if is_true(user['enabled_features']['disable_emails']):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'the emails are disabled for this user', 
            'i18n_code': 'email_disabled',
            'cid': get_current_cid()
        }, status_code = 400)

    min_amount = get_min_amount()
    if total_to_pay > min_amount:
        final_amount = int(round(total_to_pay, 4) * 100)
        send_relaunch_email(user['email'], total_to_pay, invoice.ref)
        return JSONResponse(content = {
            'status': 'ok',
            'message': 'relaunch mail successfully sent', 
            'amount_to_pay': final_amount
        }, status_code = 200)
    else:
        return JSONResponse(content = {
            'status': 'ok',
            'message': 'nothing to pay'
        }, status_code = 200)

def pay(db, user, invoice, voucher_id = "", auto_pay = False):
    registeredVoucher = None
    voucher = None
    reducted_voucher_amount = 0
    exist_voucher = False
    total_ht = 0
    total_ttc = invoice.total_price
    if total_ttc is None:
        total_ttc = 0
        from entities.Invoice import Invoice
        Invoice.updateInvoiceTotalPrice(invoice.id, total_ttc, db)

    total_to_pay = total_ttc

    if is_true(user['enabled_features']['without_vat']):
        total_ht = total_ttc
    else:
        total_ht = round(total_ttc / float(os.getenv('TTVA')), 4)

    if is_false(user['enabled_features']['billable']):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'user not billable', 
            'i18n_code': 'not_billable',
            'cid': get_current_cid()
        }, status_code = 400)

    from entities.RegisteredVoucher import RegisteredVoucher
    if is_not_empty(voucher_id):
        registeredVoucher = RegisteredVoucher.getUserRegisteredVoucher(user['id'], voucher_id, db)
        if not registeredVoucher:
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'voucher not found', 
                'i18n_code': 'voucher_not_found',
                'cid': get_current_cid()
            }, status_code = 404)
        created_registered_voucher   = datetime.datetime.fromisoformat(registeredVoucher.created_at)
        from entities.Voucher import Voucher
        voucher = Voucher.getById(registeredVoucher.voucher_id, db)
        if is_duration_valid(voucher.validity):
            validity_date = created_registered_voucher + datetime.timedelta(days = voucher.validity)
            now_date = datetime.datetime.now()
            if now_date >= validity_date:
                return JSONResponse(content = {
                    'status': 'ko',
                    'error': 'voucher has expired', 
                    'i18n_code': 'voucher_expired',
                    'cid': get_current_cid()
                }, status_code = 400)

        if registeredVoucher.credit >= total_ttc:
            reducted_voucher_amount = registeredVoucher.credit - total_ttc
            total_to_pay = 0
            exist_voucher = True
            from entities.Invoice import Invoice
            Invoice.makeInvoiceAsPaid(invoice.id, db)
        else:
            reducted_voucher_amount = 0
            exist_voucher = True
            total_to_pay = total_ttc - registeredVoucher.credit
        RegisteredVoucher.updateRegisteredVoucherCredit(voucher_id, user['id'], reducted_voucher_amount, db)

    voucher_amount = total_ttc - total_to_pay
    min_amount = get_min_amount()
    if voucher:
        name_file = generate_receipt_pdf(invoice.ref, invoice.date_created, user, total_ht, total_ttc, total_to_pay, voucher_amount, voucher.code, exist_voucher)
    else:
        name_file = generate_receipt_pdf(invoice.ref, invoice.date_created, user, total_ht, total_ttc, total_to_pay, 0, None, False)

    try:
        encoded_string = ""
        with open(name_file, 'rb') as pdf_file:
            encoded_string = base64.b64encode(pdf_file.read()).decode()
        pdf_file.close()
        log_msg("INFO", f"[api_invoice] Created new receipt of invoice {invoice.ref} for user {user['email']}")
        quiet_remove(name_file)
        log_msg("INFO", f"[api_invoice] User {user['email']} will pay {total_to_pay}")
        if total_to_pay > min_amount:
            final_amount = int(round(total_to_pay, 4) * 100)
            intent = PAYMENT_ADAPTER().payment_request(
                { 'final_amount': final_amount, 'currency': get_payment_currency() },
                user,
                invoice,
                exist_voucher,
                voucher_id,
                reducted_voucher_amount,
                auto_pay
            )
    
            return JSONResponse(content = {
                'file_name': name_file,
                'blob': str(encoded_string),
                "message": "payment successfully made",
                'client_secret': intent['client_secret'],
                'payment_method': user['st_payment_method_id'] if 'st_payment_method_id' in user else "",
                'payment_url': intent['payment_url'] if 'payment_url' in intent else "",
                'partner': intent['partner'] if 'partner' in intent else ""
            }, status_code = 200)
        else:
            return JSONResponse(content = {
                'status': 'ok',
                'file_name': name_file, 
                'blob': str(encoded_string), 
                'message': 'payment successfully made'
            }, status_code = 200)
    except HTTPError as e:
        return JSONResponse(content = {
            'status': 'ko',
            'error': e.msg, 
            'i18n_code': e.headers['i18n_code'],
            'cid': get_current_cid()
        }, status_code = e.code)
