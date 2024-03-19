from fastapi import Depends, APIRouter, Request
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

from database.postgres_db import get_db
from exceptions.CwHTTPException import CwHTTPException

from utils.common import is_empty, is_true
from utils.logger import log_msg
from utils.payment import PAYMENT_ADAPTER
from utils.observability.cid import get_current_cid
from utils.observability.otel import get_otel_tracer
from utils.observability.traces import span_format
from utils.observability.counter import create_counter, increment_counter
from utils.observability.enums import Method

router = APIRouter()

_span_prefix = "paymentwebhook"
_counter = create_counter("payment_webhook_api", "Payment webhook API counter")

@router.post("")
async def payment_webhook(request: Request, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.POST)):
        increment_counter(_counter, Method.POST)

        payload = await request.body()
        signature = request.headers.get(PAYMENT_ADAPTER().signature_header(), None)
        if is_empty(signature) and PAYMENT_ADAPTER().is_signature_required():
            log_msg("WARN", "[api_wehbook] try to invoke the webhook without signature header. Headers = {}".format(request.headers))
            raise CwHTTPException(message = {"error": "no Signature Header !"}, status_code = 400)

        event = PAYMENT_ADAPTER().decode_webhook_event(payload, signature)

        if event["code"] != 200 and "reason" in event:
            log_msg("WARN", "[api_wehbook] error on request because: code = {}, reason = {}".format(event["code"], event["reason"]))
            raise CwHTTPException(message = {"error": event["reason"]}, status_code = int(event["code"]))

        if is_true(event["succeed"]):
            email = event["receipt_email"]
            invoice_id = event["invoice_id"]
            user_id = event["user_id"]
            with_voucher = event["with_voucher"]

            from entities.Invoice import Invoice
            Invoice.makeInvoiceAsPaid(invoice_id, db)
            if is_true(with_voucher):
                voucher_id = event["voucher_id"]
                reducted_voucher_amount = event["reducted_voucher_amount"]
                from entities.RegisteredVoucher import RegisteredVoucher
                RegisteredVoucher.updateRegisteredVoucherCredit(voucher_id, user_id, reducted_voucher_amount, db)
            log_msg("INFO", "[api_wehbook] payment succeeded of invoice #{} by user {}".format(invoice_id, email))
            return JSONResponse(content = {
                'status': 'ok' if is_true(event['succeed']) else 'ko'
            }, status_code = 200)
        else:
            return JSONResponse(content = {
                'status': 'ok' if is_true(event['succeed']) else 'ko',
                'message': "the event type {} might be not known".format(event["type"]),
                'cid': get_current_cid()
            }, status_code = 200)
