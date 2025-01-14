import os
import importlib

from minio import Minio
from minio.error import S3Error
from time import sleep

from entities.Bucket import Bucket

from utils.logger import log_msg
from utils.observability.cid import get_current_cid
from utils.provider import get_driver
from utils.constants import MAX_RETRY, WAIT_TIME

def register_bucket(hash, provider, region, chosen_user_id, current_user_id, bucket_name, bucket_type, db):
    from entities.Bucket import Bucket
    new_bucket = Bucket()
    new_bucket.hash = hash
    new_bucket.name = bucket_name
    new_bucket.type = bucket_type
    new_bucket.bucket_user_id = chosen_user_id
    new_bucket.user_id = current_user_id
    new_bucket.region = region
    new_bucket.provider = provider
    new_bucket.save(db)
    return new_bucket

def delete_bucket(provider, bucket, user_email, retry = 0):
    try:
        if retry >= MAX_RETRY:
            log_msg("WARN", "[delete_bucket] max retries has been reached : provider = {}, bucket = {}, user_email = {}".format(provider, bucket, user_email))
            return

        if retry > 0:
            waiting_time = WAIT_TIME * retry
            log_msg("DEBUG", "[delete_bucket] waiting: provider = {}, bucket = {}, user_email = {}, wait = {}".format(provider, bucket, user_email, waiting_time))
            sleep(waiting_time)

        ProviderDriverModule = importlib.import_module('drivers.{}'.format(get_driver(provider)))
        ProviderDriver = getattr(ProviderDriverModule, get_driver(provider))
        ProviderDriver().delete_bucket(bucket, user_email)
    except Exception as e:
        log_msg("WARN", "[delete_bucket] trying again because of this error: provider = {}, bucket = {}, user_email = {}, error = {}".format(provider, bucket, user_email, e))
        delete_bucket(provider, bucket, user_email, retry + 1)

def update_credentials(provider, bucket, db):
    ProviderDriverModule = importlib.import_module('drivers.{}'.format(get_driver(provider)))
    ProviderDriver = getattr(ProviderDriverModule, get_driver(provider))
    result = ProviderDriver().update_bucket_credentials(bucket)
    Bucket.updateCredentials(bucket.id, result["access_key"], result["secret_key"], db)

def refresh_bucket(user_email, provider, bucket_id, hashed_bucket_name, db):
    ProviderDriverModule = importlib.import_module('drivers.{}'.format(get_driver(provider)))
    ProviderDriver = getattr(ProviderDriverModule, get_driver(provider))
    result = ProviderDriver().refresh_bucket(user_email, hashed_bucket_name)
    if "type" in result:
        Bucket.updateType(bucket_id, result['type'], db)

def create_bucket(provider, user_email, bucket_id, hashed_bucket_name, region, bucket_type, db):
    ProviderDriverModule = importlib.import_module('drivers.{}'.format(get_driver(provider)))
    ProviderDriver = getattr(ProviderDriverModule, get_driver(provider))
    result = ProviderDriver().create_bucket(user_email, hashed_bucket_name, region, bucket_type)
    log_msg("DEBUG", "[create_bucket] driver result = {}".format(result))
    Bucket.update(bucket_id, result['endpoint'], result['user_id'] if "user_id" in result else None, result['access_key'], result['secret_key'], "active", db)

access_key = os.getenv('SCW_ACCESS_KEY')
secret_key = os.getenv('SCW_SECRET_KEY')
bucket_region = os.getenv('BUCKET_REGION')

invoice_bucket_url = os.getenv('BUCKET_URL')
invoice_bucket_name = os.getenv('BUCKET_NAME')

attachment_bucket_url = os.getenv('ATTACHMENT_BUCKET_URL', invoice_bucket_url)
attachment_bucket_name = os.getenv('ATTACHMENT_BUCKET_NAME', invoice_bucket_name)

def upload_to_attachment_bucket(target_name, file_path):
    upload_bucket(target_name, file_path, attachment_bucket_url, attachment_bucket_name)

def download_from_attachment_bucket(target_name, file_path):
    return download_from_bucket(target_name, file_path, attachment_bucket_url, attachment_bucket_name)

def delete_from_attachment_bucket(target_name, file_path):
    return delete_from_bucket(target_name, file_path, attachment_bucket_url, attachment_bucket_name)

def upload_to_invoices_bucket(target_name, file_path):
    upload_bucket(target_name, file_path, invoice_bucket_url, invoice_bucket_name)

def download_from_invoices_bucket(target_name, file_path):
    return download_from_bucket(target_name, file_path, invoice_bucket_url, invoice_bucket_name)

def upload_bucket(target_name, file_path, url, bucket_name):
    if url and access_key and secret_key and bucket_name and bucket_region:
        client = Minio(url, region = bucket_region, access_key = access_key, secret_key = secret_key)
        found = client.bucket_exists(bucket_name)
        log_msg("DEBUG", "[upload_bucket] found = {}".format(found))
        if not found:
            client.make_bucket(bucket_name)
        client.fput_object(bucket_name, target_name, file_path)

def download_from_bucket(target_name, file_path, url, bucket_name):
    if url and access_key and secret_key and bucket_name and bucket_region:
        try:
            client = Minio(url, region = bucket_region, access_key = access_key, secret_key = secret_key)
            client.fget_object(bucket_name, target_name, file_path)
            return {
                'status': 'ok',
            }
        except S3Error as e:
            not_found_msg = "File not found: target_name = {}, file_path = {}".format(target_name, file_path)
            log_msg("WARN", "[bucket][download_from_bucket] {}, e = {}".format(not_found_msg, e))
            return {
                'status': 'ko',
                'message': not_found_msg,
                'i18n_code': 'file_not_found',
                'http_code': 404,
                'cid': get_current_cid()
            }
        
def delete_from_bucket(target_name, file_path, url, bucket_name):
    if url and access_key and secret_key and bucket_name and bucket_region:
        try:
            client = Minio(url, region = bucket_region, access_key = access_key, secret_key = secret_key)
            client.remove_object(bucket_name, target_name)
            return {
                'status': 'ok',
            }
        except S3Error as e:
            not_found_msg = "File not found: target_name = {}, file_path = {}".format(target_name, file_path)
            log_msg("WARN", "[bucket][delete_from_bucket] {}, e = {}".format(not_found_msg, e))
            return {
                'status': 'ko',
                'message': not_found_msg,
                'i18n_code': 'file_not_found',
                'http_code': 404,
                'cid': get_current_cid()
            }
