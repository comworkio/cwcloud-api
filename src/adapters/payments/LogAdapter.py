from adapters.payments.PaymentAdapter import PaymentAdapter
from utils.logger import log_msg
from utils.webhook import unmarshall_payload

class LogAdapter(PaymentAdapter):
    def is_disabled(self):
        is_disabled = False
        log_msg("INFO", "[Payments][LogAdapter][is_disabled] is_disabled = {}".format(is_disabled))
        return is_disabled

    def signature_header(self):
        header = "X-Comwork-Payments-Signature"
        log_msg("INFO", "[Payments][LogAdapter][signature_header] header = {}".format(header))
        return header

    def is_signature_required(self):
        required = False
        log_msg("INFO", "[Payments][LogAdapter][is_signature_required] required = {}".format(required))
        return required

    def retrieve_payment_method(self, payment_method_id):
        retrieve = True
        log_msg("INFO", "[Payments][LogAdapter][retrieve] payment_method_id = {}, retrieve = {}".format(payment_method_id, retrieve))
        return retrieve

    def attach_payment_method(self, payment_method, user):
        attach = True
        log_msg("INFO", "[Payments][LogAdapter][attach] payment_method = {}, attach = {}".format(payment_method, attach))
        return attach

    def detach_payment_method(self, payment_method_id):
        detach = True
        log_msg("INFO", "[Payments][LogAdapter][detach] payment_method_id = {}, detach = {}".format(payment_method_id, detach))
        return detach

    def list_payment_methods(self, user):
        payment_methods = []
        log_msg("INFO", "[Payments][LogAdapter][list_payment_methods] user = {}, payment_methods = {}".format(user, payment_methods))
        return payment_methods

    def create_customer(self, email):
        customer = { "id": "" }
        log_msg("INFO", "[Payments][LogAdapter][create_customer] email = {}, customer = {}".format(email, customer))
        return customer

    def payment_request(self, request, user, invoice, exist_voucher, voucher_id, reducted_voucher_amount, auto_pay):
        intent = {
            'id': "",
            'client_secret': "",
            'payment_url': '',
            'partner': 'log',
            'confirm': auto_pay
        }
        log_msg("INFO", "[Payments][LogAdapter][payment_request] request = {}, user_id = {}, invoice_id = {}, exist_voucher = {}, voucher_id = {}, reducted_voucher_amount = {}, intent = {}".format(request, user['id'], invoice.id, exist_voucher, voucher_id, reducted_voucher_amount, intent))
        return intent

    def decode_webhook_event(self, payload, signature):
        response = {
            "code": 405,
            "message": "Not implemented"
        }
        log_msg("INFO", "[Payments][LogAdapter][decode_webhook_event] payload = {}, signature = {}, response = {}".format(unmarshall_payload(payload), signature, response))
        return response
