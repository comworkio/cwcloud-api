import os
import re
import pdfkit

from datetime import datetime
from decimal import Decimal

from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

from utils.bucket import upload_bucket
from utils.common import is_empty, is_not_empty, is_true

from entities.Invoice import Invoice

def generate_invoice_pdf(invoice_ref, client, consumptions, subscriptions, from_date, to_date, total_ht, total_ttc, without_tva):
    invoice_date = str(datetime.now()).split(" ")[0]

    file_loader = FileSystemLoader(str(Path(__file__).resolve().parents[1]) + '/templates')
    env = Environment(loader = file_loader)

    template = env.get_template("invoice.j2")
    company_name = "Particulier"
    registration_number = ""
    if is_not_empty(client.company_name):
        company_name = client.company_name

    if is_not_empty(client.registration_number):
        registration_number = client.registration_number
    elif is_empty(client.company_name):
        registration_number = "Particulier"

    ttva = os.getenv('TTVA')
    if is_empty(ttva):
        ttva = "1.2"

    price_unit = os.getenv('PRICE_UNIT')
    if is_empty(price_unit):
        price_unit = "Euros"

    invoice_company_signature = os.getenv('INVOICE_COMPANY_SIGNATURE')
    invoice_company_logo = os.getenv('INVOICE_COMPANY_LOGO')
    invoice_company_registration_number = os.getenv('INVOICE_COMPANY_REGISTRATION_NUMBER')
    invoice_company_city = os.getenv('INVOICE_COMPANY_CITY')
    invoice_company_address = os.getenv('INVOICE_COMPANY_ADDRESS')
    invoice_company_contact = os.getenv('INVOICE_COMPANY_CONTACT')
    invoice_company_email = os.getenv('INVOICE_COMPANY_EMAIL')
    registration_number_label = os.getenv('REGISTRATION_NUMBER_LABEL')
    if is_empty(registration_number_label):
        registration_number_label = "N° SIRET"

    vat_message = "{}%".format((Decimal(ttva)-1)*100)
    timbre_fiscal = os.getenv('TIMBRE_FISCAL')
    timbre_fiscal_message = None
    if is_true(without_tva):
        vat_message = "Pas de TVA"
    elif is_not_empty(timbre_fiscal):
        timbre_fiscal_message = "{} {}".format(timbre_fiscal, price_unit)

    pdf_content = template.render(
        invoice_ref = invoice_ref,
        invoice_date = invoice_date,
        company_name = company_name,
        registration_number = registration_number,
        registration_number_label = registration_number_label,
        invoice_company_signature = invoice_company_signature,
        invoice_company_logo = invoice_company_logo,
        invoice_company_registration_number = invoice_company_registration_number,
        invoice_company_address = invoice_company_address,
        invoice_company_city = invoice_company_city,
        invoice_company_contact = invoice_company_contact,
        invoice_company_email = invoice_company_email,
        timbre_fiscal_message = timbre_fiscal_message,
        address = client.address,
        contact = client.contact_info,
        email = client.email,
        consumptions = consumptions,
        subscriptions = subscriptions,
        from_date = from_date,
        to_date = to_date,
        total_ht = total_ht,
        total_ttc = total_ttc,
        price_unit = price_unit,
        vat_message = vat_message
    )

    name_file = "invoice_{}_{}.pdf".format(invoice_ref, client.id)
    options = {
        "enable-local-file-access": ""
    }
    pdfkit.from_string(pdf_content, name_file, options = options)
    return name_file

def generate_receipt_pdf(invoice_ref, invoice_date, client, total_ht, total_ttc, amount_cart, amount_voucher, voucher_code, with_voucher):
    file_loader = FileSystemLoader(str(Path(__file__).resolve().parents[1]) + '/templates')
    env = Environment(loader = file_loader)

    template = env.get_template("receipt.j2")
    company_name = "Particulier"
    registration_number = ""
    if is_not_empty(client['company_name']):
        company_name = client['company_name']

    if is_not_empty(client['registration_number']):
        registration_number = client['registration_number']
    elif is_empty(client['company_name']):
        registration_number = "Particulier"

    ttva = os.getenv('TTVA')
    if is_empty(ttva):
        ttva = "1.2"

    vat_message = "{}%".format((Decimal(ttva)-1)*100)

    timbre_fiscal = os.getenv('TIMBRE_FISCAL')
    timbre_fiscal_message = None

    price_unit = os.getenv('PRICE_UNIT')
    if is_empty(price_unit):
        price_unit = "Euros"

    if is_true(client['enabled_features']['without_vat']):
        vat_message = "Pas de TVA"
    elif is_not_empty(timbre_fiscal):
        timbre_fiscal_message = "{} {}".format(timbre_fiscal_message, price_unit)

    invoice_company_signature = os.getenv('INVOICE_COMPANY_SIGNATURE')
    invoice_company_logo = os.getenv('INVOICE_COMPANY_LOGO')
    invoice_company_registration_number = os.getenv('INVOICE_COMPANY_REGISTRATION_NUMBER')
    invoice_company_city = os.getenv('INVOICE_COMPANY_CITY')
    invoice_company_address = os.getenv('INVOICE_COMPANY_ADDRESS')
    invoice_company_contact = os.getenv('INVOICE_COMPANY_CONTACT')
    invoice_company_email = os.getenv('INVOICE_COMPANY_EMAIL')
    registration_number_label = os.getenv('REGISTRATION_NUMBER_LABEL')
    if is_empty(registration_number_label):
        registration_number_label = "N° SIRET"

    pdf_content = template.render(
        invoice_ref = invoice_ref,
        invoice_date = invoice_date,
        company_name = company_name,
        registration_number = registration_number,
        registration_number_label = registration_number_label,
        invoice_company_signature = invoice_company_signature,
        invoice_company_logo = invoice_company_logo,
        invoice_company_registration_number = invoice_company_registration_number,
        invoice_company_address = invoice_company_address,
        invoice_company_city = invoice_company_city,
        invoice_company_contact = invoice_company_contact,
        invoice_company_email = invoice_company_email,
        timbre_fiscal_message = timbre_fiscal_message,
        address = client['address'],
        contact = client['contact_info'],
        email = client['email'],
        total_ht = total_ht,
        total_ttc = total_ttc,
        vat_message = vat_message,
        amount_cart = amount_cart,
        amount_voucher = amount_voucher,
        price_unit = price_unit,
        voucher_code = voucher_code,
        with_voucher = with_voucher
    )

    name_file = "receipt_{}_{}.pdf".format(invoice_ref, client['id'])
    options = {
        "enable-local-file-access": ""
    }
    pdfkit.from_string(pdf_content, name_file, options = options)
    path_file = "{}/{}".format(datetime.fromisoformat(str(invoice_date)).strftime('%Y-%m'), name_file)
    upload_bucket(path_file, name_file)
    return name_file

def increase_invoice_number(current_year, max_invoice_ref):
    _zfill_size = 5
    if is_empty(max_invoice_ref):
        incr_without_year = "1".zfill(_zfill_size)
    else:
        incr = int(max_invoice_ref) + 1
        incr_without_year = re.sub(f"^{current_year}", "", str(incr)).zfill(_zfill_size)

    return f'{current_year}{incr_without_year}'

def get_invoice_ref(db):
    current_year = datetime.now().strftime("%Y")
    max_invoice_ref = Invoice.getMaxInvoiceRef(current_year, db)
    return increase_invoice_number(current_year, max_invoice_ref)

def add_subscription(is_api_enabled, env_var_name, label, subscriptions):
    email_api_price = os.getenv(env_var_name)
    if is_api_enabled and is_not_empty(email_api_price):
        float_price = float(os.getenv(env_var_name))
        subscriptions.append({
            "label": label,
            "price": float_price
        })
        return float_price
    return 0
