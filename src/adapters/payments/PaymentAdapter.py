from abc import ABC, abstractmethod

class PaymentAdapter(ABC):
    @abstractmethod
    def is_disabled(self):
        pass

    @abstractmethod
    def signature_header(self):
        pass

    @abstractmethod
    def is_signature_required(self):
        pass

    @abstractmethod
    def retrieve_payment_method(self, payment_method_id):
        pass

    @abstractmethod
    def attach_payment_method(self, payment_method, user):
        pass

    @abstractmethod
    def detach_payment_method(self, payment_method_id):
        pass

    @abstractmethod
    def list_payment_methods(self, user):
        pass

    @abstractmethod
    def create_customer(self, email):
        pass

    @abstractmethod
    def payment_request(self, request, user, invoice, exist_voucher, voucher_id, reducted_voucher_amount, auto_pay):
        pass

    @abstractmethod
    def decode_webhook_event(self, payload, signature):
        pass
