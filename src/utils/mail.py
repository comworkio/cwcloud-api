from urllib.error import HTTPError
import os
from datetime import datetime
from datetime import datetime
from adapters.AdapterConfig import get_adapter, get_default_adapter
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from utils.bucket import upload_bucket
from utils.common import is_empty, is_not_empty, is_true
from utils.logger import log_msg
import re

EMAIL_EXPEDITOR = os.environ['EMAIL_EXPEDITOR']
EMAIL_ACCOUNTING = os.getenv('EMAIL_ACCOUNTING') if is_not_empty(os.getenv('EMAIL_ACCOUNTING')) else EMAIL_EXPEDITOR
EMAIL_ADAPTER = get_adapter("emails")
DEFAULT_EMAIL_ADAPTER = get_default_adapter("emails")

current_year = datetime.now().year

def send_confirmation_email(receiver_email, activateLink, subject):
    log_msg("INFO", "[send_confirmation_email] activateLink = {}".format(activateLink))
    if EMAIL_ADAPTER().is_disabled():
        return {}

    file_loader = FileSystemLoader(str(Path(__file__).resolve().parents[1]) + '/templates')
    env = Environment(loader = file_loader)
    template = env.get_template('confirmation_mail.j2')
    content = template.render(
        activateLink = activateLink,
        currentYear = current_year
    )
    log_msg("INFO", "[send_email] Send from = {}, to = {}, content = {}".format(EMAIL_EXPEDITOR, receiver_email, activateLink))
    return EMAIL_ADAPTER().send({
        'from': EMAIL_EXPEDITOR,
        'to': receiver_email,
        'content': content,
        'subject': subject
    })

def send_forget_password_email(receiver_email, activateLink, subject):
    log_msg("INFO", "[send_forget_password_email] activateLink = {}".format(activateLink))
    if EMAIL_ADAPTER().is_disabled():
        return {}

    file_loader = FileSystemLoader(str(Path(__file__).resolve().parents[1]) + '/templates')
    env = Environment(loader = file_loader)
    template = env.get_template('forget_password_mail.j2')
    content = template.render(
        activateLink = activateLink,
        currentYear = current_year
    )
    log_msg("INFO", "[send_email] Send from = {}, to = {}, link = {}".format(EMAIL_EXPEDITOR, receiver_email, activateLink))
    return EMAIL_ADAPTER().send({
        'from': EMAIL_EXPEDITOR,
        'to': receiver_email,
        'content': content,
        'subject': subject
    })

def send_templated_email(email):
    if EMAIL_ADAPTER().is_disabled():
        return {}

    file_loader = FileSystemLoader(str(Path(__file__).resolve().parents[1]) + '/templates')
    env = Environment(loader = file_loader)
    template = env.get_template('email.j2')
    content = template.render(
        body = email['content'],
        title = email['subject'],
        currentYear = current_year
    )
    email['content'] = content
    return EMAIL_ADAPTER().send(email)

def send_email(receiver_email, body, subject):
    return send_templated_email({
        'from': EMAIL_EXPEDITOR,
        'to': receiver_email,
        'content': body,
        'subject': subject
    })

def send_contact_email(from_email, receiver_email, body, subject):
    if EMAIL_ADAPTER().is_disabled():
        return {}

    file_loader = FileSystemLoader(str(Path(__file__).resolve().parents[1]) + '/templates')
    env = Environment(loader = file_loader)
    template = env.get_template('email.j2')
    content = template.render(
        body = body,
        title = subject,
        currentYear = current_year
    )

    log_msg("INFO", "[send_contact_email] Send from = {}, to = {}, content = {}".format(from_email, receiver_email, body))
    return EMAIL_ADAPTER().send({
        'from': from_email,
        'to': receiver_email,
        'content': content,
        'subject': subject
    })

def send_relaunch_email(email, total_to_pay, invoice_ref):
    if EMAIL_ADAPTER().is_disabled():
        return {}

    subject = "Payment issue cwcloud"

    price_unit = os.getenv('PRICE_UNIT')
    if is_empty(price_unit):
        price_unit = "Euros"

    message = "<p>There is an issue with the payment of your invoice {} with an amount of {} {}.</p>".format(invoice_ref, total_to_pay, price_unit.lower()) + \
        "<p>This problem can occur if you have a 3DSecure security notification that has been sent and not confirmed or if there are not enough funds in your payment method.</p>"

    billing_url = os.getenv('BILLING_PROCEDURE_URL')
    if is_not_empty(billing_url):
        message += "<p>You'll have to proceed to the payment manually following <a href = \"{}\">this procedure</a>.</p>".format(billing_url)

    file_loader = FileSystemLoader(str(Path(__file__).resolve().parents[1]) + '/templates')
    env = Environment(loader = file_loader)
    template = env.get_template('email.j2')
    content = template.render(body = message, currentYear = current_year)

    return EMAIL_ADAPTER().send({
        'from': EMAIL_EXPEDITOR,
        'to': email,
        'bcc': EMAIL_ACCOUNTING,
        'content': content,
        'subject': subject
    })

def send_invoice_email(email, file_name, encoded_file, send, edition = False, date_path = datetime.now().strftime('%Y-%m')):
    if EMAIL_ADAPTER().is_disabled():
        return {}

    message = "<p> Your monthly invoice is available. Please find the PDF document attached at the bottom of this email. <p>"
    subject = "Invoice cwcloud"
    if edition:
        subject = "Edited invoice cwcloud"
        message = "<p> Your previous invoice has been edited. Please find the PDF document attached at the bottom of this email. <p>"

    file_loader = FileSystemLoader(str(Path(__file__).resolve().parents[1]) + '/templates')
    env = Environment(loader = file_loader)
    template = env.get_template('email.j2')
    content = template.render(body = message, currentYear = current_year)

    email_payload = {
        'from': EMAIL_EXPEDITOR,
        'to': email,
        'bcc': EMAIL_ACCOUNTING,
        'content': content,
        'subject': subject,
        'attachment': {
            'content': encoded_file,
            'mime_type': 'application/pdf',
            'file_name': file_name
        }
    }

    try:
        response = EMAIL_ADAPTER().send(email_payload) if is_true(send) else DEFAULT_EMAIL_ADAPTER().send(email_payload)
        log_msg("DEBUG", "[mail][send_invoice_email] file_name = {}, date_path = {}".format(file_name, date_path))
        path_file = "{}/{}".format(date_path, file_name)
        upload_bucket(path_file, file_name)
        return response
    except Exception as ex:
        log_msg("ERROR", "[mail] unexpected error : type = {}, file = {}, lno = {}, msg = {}".format(type(ex).__name__, __file__, ex.__traceback__.tb_lineno, ex))
        raise HTTPError("1114", 409, 'could not send invoice pdf email', hdrs = {"i18n_code": "1112"}, fp = None)

def send_create_instance_email(user_email, project_repo_url, instance_name, environment, access_password, root_dns_zone):
    if EMAIL_ADAPTER().is_disabled():
        return {}

    instance_url = "https://{}.{}.{}".format(instance_name, environment['path'], root_dns_zone)
    subject = "New Cloud instance access information"
    message_tpl = "Cloud instance information: <ul>" + \
        "<li>Environment: {}</li>" + \
        "<li>Instance name: {}</li>" + \
        "<li>Instance domain: {}</li>" + \
        "<li>Access password: {}</li>" + \
        "<li>GitLab repository URL: {}</li>" + \
        "</ul>"
    message = message_tpl.format(environment['name'], instance_name, instance_url, access_password, project_repo_url)

    return send_email(user_email, message, subject)

def send_reply_to_customer_email(customer_email, subject, reply_message):
    if EMAIL_ADAPTER().is_disabled():
        return {}

    subject = "Re: " + subject
    message_tpl = "You have a new reply to your support ticket: <ul>" + \
        "<li>Subject: {}</li>" + \
        "<li>Message: {}</li>" + \
        "</ul>"
    message = message_tpl.format(subject, reply_message)

    return send_email(customer_email, message, subject)
