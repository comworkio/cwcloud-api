import os
import stripe

from adapters.payments.PaymentAdapter import PaymentAdapter
from utils import common
from utils.logger import log_msg

_stripe_api_key = os.getenv('STRIPE_API_KEY')

class StripeAdapter(PaymentAdapter):
    def is_disabled(self):
        return common.is_disabled(_stripe_api_key)

    def signature_header(self):
        return "stripe-signature"

    def is_signature_required(self):
        return True

    def create_customer_and_update_user(self, email):
        try:
            if self.is_disabled():
                log_msg("DEBUG", "[Payments][StripeAdapter][create_customer_and_update_user] stripe is disabled")
                return { "id": "" }
            stripe.api_key = _stripe_api_key
            customer = stripe.Customer.create(description = email, email = email)
            from entities.User import User
            User.updateCustomerId(email, customer['id'])
            return customer

        except Exception as ae:
            log_msg("ERROR", "[Payments][StripeAdapter][create_customer_and_update_user] error: {}".format(ae))
            return { "id": "" }

    def check_customer_exist_or_create(self, email, customerId):
        if common.is_empty(customerId):
            log_msg("DEBUG", "[Payments][StripeAdapter][check_customer_exist_or_create] customer with email {} does not exist, creating a new customer".format(email))
            customer = self.create_customer_and_update_user(email)
            return customer['id']
        try:
            stripe.api_key = _stripe_api_key
            customer = stripe.Customer.retrieve(customerId)
            return customer['id']

        except stripe.error.StripeError as e:
            if e.code == "resource_missing":
                log_msg("DEBUG", "[Payments][StripeAdapter][check_customer_exist_or_create] customer {} with id {} does not exist, creating a new customer".format(email, customerId))
                customer = self.create_customer_and_update_user(email)
                return customer['id']

    def attach_payment_method(self, payment_method, user):
        try:
            if self.is_disabled():
                log_msg("DEBUG", "[Payments][StripeAdapter][attach] stripe is disabled")
                return True
            customer_id = self.check_customer_exist_or_create(user.email, user.st_customer_id)
            stripe.api_key = _stripe_api_key
            stripe.PaymentMethod.attach(payment_method, customer = customer_id)
            return True
        except Exception as ae:
            log_msg("ERROR", "[Payments][StripeAdapter][attach] error: {}".format(ae))
            return False

    def retrieve_payment_method(self, payment_method):
        try:
            if self.is_disabled():
                log_msg("DEBUG", "[Payments][StripeAdapter][retrieve] stripe is disabled")
                return True
            stripe.api_key = _stripe_api_key
            return stripe.PaymentMethod.retrieve(payment_method)
        except Exception as ae:
            log_msg("ERROR", "[Payments][StripeAdapter][retrieve] error: {}".format(ae))
            return False

    def detach_payment_method(self, payment_method_id):
        try:
            if self.is_disabled():
                log_msg("DEBUG", "[Payments][StripeAdapter][detach] stripe is disabled")
                return True
            stripe.api_key = _stripe_api_key
            stripe.PaymentMethod.detach(payment_method_id)
            return True
        except Exception as ae:
            log_msg("ERROR", "[Payments][StripeAdapter][detach] error: {}".format(ae))
            return False

    def create_customer(self, email):
        try:
            if self.is_disabled():
                log_msg("DEBUG", "[Payments][StripeAdapter][create_customer] stripe is disabled")
                return { "id": "" }
            stripe.api_key = _stripe_api_key
            return stripe.Customer.create(description = email, email = email)
        except Exception as ae:
            log_msg("ERROR", "[Payments][StripeAdapter][create_customer] error: {}".format(ae))
            return { "id": "" }

    def list_payment_methods(self, user):
        try:
            if self.is_disabled():
                log_msg("DEBUG", "[Payments][StripeAdapter][create_customer] stripe is disabled")
                return []

            customer_id = self.check_customer_exist_or_create(user.email, user.st_customer_id)
            stripe.api_key = _stripe_api_key
            return stripe.Customer.list_payment_methods(customer_id, type = "card")

        except stripe.error.StripeError as e:
            log_msg("ERROR", "[Payments][StripeAdapter][list_payment_methods] error: {}".format(e))
            return []

    def payment_request(self, request, user, invoice, exist_voucher, voucher_id, reducted_voucher_amount, auto_pay):
        if self.is_disabled():
            log_msg("DEBUG", "[Payments][StripeAdapter][payment_request] stripe is disabled")
            return { 'id': "", 'client_secret': "" }

        stripe.api_key = _stripe_api_key
        intent = stripe.PaymentIntent.create(
            amount = request['final_amount'],
            currency = request['currency'],
            customer = user['st_customer_id'],
            receipt_email = user['email'],
            payment_method = user['st_payment_method_id'],
            confirm = auto_pay,
            automatic_payment_methods = {
                "enabled": True, 
                "allow_redirects": "never"
            },
            metadata = {
                "invoice_id": invoice.id,
                "with_voucher": exist_voucher,
                "voucher_id": voucher_id,
                "reducted_voucher_amount": reducted_voucher_amount,
                "user_id": user['id']
            }
        )
        return {
            'id': intent['id'],
            'client_secret': intent['client_secret'],
            'payment_url': '',
            'partner': 'stripe'
        }

    def decode_webhook_event(self, payload, signature):
        endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        try:
            stripe.api_key = _stripe_api_key
            event = stripe.Webhook.construct_event(
                payload = payload, sig_header = signature, secret = endpoint_secret
            )

            if not 'data' in event or not 'object' in event['data'] or not 'metadata' in event['data']['object']:
                return {
                    "code": 200,
                    "succeed": False,
                    "type": event['type'] if 'type' in event else "unknown"
                }

            with_voucher = event['data']['object']['metadata']['with_voucher'] if 'with_voucher' in event['data']['object']['metadata'] else False
            voucher_id = event['data']['object']['metadata']['voucher_id'] if common.is_true(with_voucher) else None
            reducted_voucher_amount = event['data']['object']['metadata']['reducted_voucher_amount'] if common.is_true(with_voucher) else None
            receipt_email = event['data']['object']['receipt_email'] if 'receipt_email' in event['data']['object'] else None
            invoice_id = event['data']['object']['metadata']['invoice_id'] if 'invoice_id' in event['data']['object']['metadata'] else None
            user_id = event['data']['object']['metadata']['user_id'] if 'user_id' in event['data']['object']['metadata'] else None

            return {
                "code": 200,
                "succeed": event['type'] == 'payment_intent.succeeded',
                "type": event['type'],
                "receipt_email": receipt_email,
                "invoice_id": invoice_id,
                "user_id": user_id,
                "with_voucher": with_voucher,
                "voucher_id": voucher_id,
                "reducted_voucher_amount": reducted_voucher_amount
            }
        except ValueError as ve:
            return {
                "code": 400,
                "succeed": False,
                "reason": "Invalid payload"
            }
        except stripe.error.SignatureVerificationError as se:
            return {
                "code": 400,
                "succeed": False,
                "reason": "Invalid signature: signature = {}, e.msg = {}".format(signature, se)
            }
