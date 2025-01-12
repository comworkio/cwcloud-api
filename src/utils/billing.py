from datetime import datetime
from utils.bucket import download_from_invoices_bucket

from utils.common import get_env_float, is_false
from utils.logger import log_msg

TTVA = get_env_float("TTVA", 1.2)
TIMBRE_FISCAL = get_env_float("TIMBRE_FISCAL", 0.0)

def download_billing_file(kind, user_id, user_invoice):
    target_name = f"{kind}_{user_invoice.ref}_{user_id}.pdf"
    path_file = "{}/{}".format(datetime.fromisoformat(str(user_invoice.date_created)).strftime("%Y-%m"), target_name)
    log_msg("INFO", f"[download_billing_file][1] path_file = {path_file}")
    download_status = download_from_invoices_bucket(path_file, target_name)
    if is_false(download_status["status"]):
        target_name = f"{kind}_{user_invoice.ref}.pdf"
        path_file = "{}/{}".format(datetime.fromisoformat(str(user_invoice.date_created)).strftime("%Y-%m"), target_name)
        log_msg("INFO", f"[download_billing_file][2] path_file = {path_file}")
        download_status = download_from_invoices_bucket(path_file, target_name)

    log_msg("INFO", f"[download_billing_file] download_status = {download_status["status"]}")
    return target_name, download_status
