import os

from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

from adapters.AdapterConfig import get_adapter, get_default_adapter

from utils.common import is_not_empty, AUTOESCAPE_EXTENSIONS
from utils.logger import log_msg

EMAIL_EXPEDITOR = os.getenv('EMAIL_EXPEDITOR', 'cloud@changeit.com')
EMAIL_ACCOUNTING = os.getenv('EMAIL_ACCOUNTING') if is_not_empty(os.getenv('EMAIL_ACCOUNTING')) else EMAIL_EXPEDITOR
EMAIL_ADAPTER = get_adapter("emails")
DEFAULT_EMAIL_ADAPTER = get_default_adapter("emails")

current_year = datetime.now().year

def send_email_with_chosen_template(receiver_email, activateLink, subject, template):
    if EMAIL_ADAPTER().is_disabled():
        return {}

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

def send_confirmation_email(receiver_email, activateLink, subject):
    log_msg("INFO", "[send_confirmation_email] activateLink = {}".format(activateLink))
    file_loader = FileSystemLoader(str(Path(__file__).resolve().parents[1]) + '/templates')
    env = Environment(loader=file_loader, autoescape=select_autoescape(AUTOESCAPE_EXTENSIONS))
    template = env.get_template('confirmation_mail.j2')
    return send_email_with_chosen_template(receiver_email, activateLink, subject, template)

def send_device_confirmation_email(receiver_email, activateLink, subject):
    log_msg("INFO", "[send_device_confirmation_email] activateLink = {}".format(activateLink))
    file_loader = FileSystemLoader(str(Path(__file__).resolve().parents[1]) + '/templates')
    env = Environment(loader=file_loader, autoescape=select_autoescape(AUTOESCAPE_EXTENSIONS))
    template = env.get_template('/iot/device_confirmation_mail.j2')
    return send_email_with_chosen_template(receiver_email, activateLink, subject, template)

def send_user_and_device_confirmation_email(receiver_email, generated_password, activateLink, subject):
    log_msg("INFO", "[send_user_and_device_confirmation_email] activateLink = {}".format(activateLink))
    if EMAIL_ADAPTER().is_disabled():
        return {}

    file_loader = FileSystemLoader(str(Path(__file__).resolve().parents[1]) + '/templates')
    env = Environment(loader=file_loader, autoescape=select_autoescape(AUTOESCAPE_EXTENSIONS))
    template = env.get_template('/iot/user_and_device_confirmation_mail.j2')
    content = template.render(
        email = receiver_email,
        password = generated_password,
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

def send_user_confirmation_email_without_activation_link(receiver_email, generated_password, subject):
    log_msg("INFO", "[send_user_confirmation_email_without_activation_link] generated_password = {}".format(generated_password))
    if EMAIL_ADAPTER().is_disabled():
        return {}

    file_loader = FileSystemLoader(str(Path(__file__).resolve().parents[1]) + '/templates')
    env = Environment(loader=file_loader, autoescape=select_autoescape(AUTOESCAPE_EXTENSIONS))
    template = env.get_template('/confirmation_mail_without_activation_link.j2')
    content = template.render(
        password = generated_password,
        currentYear = current_year
    )
    log_msg("INFO", "[send_email] Send from = {}, to = {}, content = {}".format(EMAIL_EXPEDITOR, receiver_email, generated_password))
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
    env = Environment(loader=file_loader, autoescape=select_autoescape(AUTOESCAPE_EXTENSIONS))
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
    env = Environment(loader=file_loader, autoescape=select_autoescape(AUTOESCAPE_EXTENSIONS))
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
    env = Environment(loader=file_loader, autoescape=select_autoescape(AUTOESCAPE_EXTENSIONS))
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
