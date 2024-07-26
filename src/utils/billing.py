from datetime import datetime
from utils.bucket import download_from_invoices_bucket

from utils.common import is_false

def download_billing_file(kind, user_id, user_invoice):
    target_name = f"{kind}_{user_invoice.ref}_{user_id}.pdf"
    path_file = "{}/{}".format(datetime.fromisoformat(str(user_invoice.date_created)).strftime("%Y-%m"), target_name)
    download_status = download_from_invoices_bucket(path_file, target_name)
    if is_false(download_status["status"]):
        target_name = f"{kind}_{user_invoice.ref}.pdf"
        path_file = "{}/{}".format(datetime.fromisoformat(str(user_invoice.date_created)).strftime("%Y-%m"), target_name)
        download_status = download_from_invoices_bucket(path_file, target_name)

    return target_name, download_status
