import json

from urllib.error import HTTPError
from fastapi import BackgroundTasks
from fastapi.responses import JSONResponse

from utils.bucket import delete_bucket, update_credentials
from utils.common import is_empty, is_numeric
from utils.encoder import AlchemyEncoder
from utils.observability.cid import get_current_cid
from utils.provider import exist_provider

def get_bucket(current_user, provider, region, bucket_id, db):
    if not exist_provider(provider):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'provider does not exist',
            'i18n_code': 'provider_not_exist',
            'cid': get_current_cid()
        }, status_code = 404)

    if not is_numeric(bucket_id):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Invalid bucket id',
            'i18n_code': 'invalid_payment_method_id',
            'cid': get_current_cid()
        }, status_code = 400)

    from entities.Bucket import Bucket
    user_bucket = Bucket.findUserBucket(provider, current_user.id, bucket_id, region, db)
    if not user_bucket:
        from entities.Access import Access
        access = Access.getUserAccessToObject(current_user.id, "bucket", bucket_id, db)
        if not access:
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'Bucket not found',
                'i18n_code': '2fa_method_not_found',
                'cid': get_current_cid()
            }, status_code = 404)
        user_bucket = Bucket.findBucket(provider, region, access.object_id, db)
    dumpedBucket = json.loads(json.dumps(user_bucket, cls = AlchemyEncoder))
    return JSONResponse(content = dumpedBucket, status_code = 200)

def remove_bucket(current_user, provider, region, bucket_id, db, bt: BackgroundTasks):
    if not exist_provider(provider):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'provider does not exist',
            'i18n_code': 'provider_not_exist',
            'cid': get_current_cid()
        }, status_code = 404)
    if not is_numeric(bucket_id):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Invalid bucket id',
            'i18n_code': 'invalid_payment_method_id',
            'cid': get_current_cid()
        }, status_code = 400)
    from entities.Bucket import Bucket
    user_bucket = Bucket.findUserBucket(provider, current_user.id, bucket_id, region, db)
    if not user_bucket:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Bucket not found',
            'i18n_code': '2fa_method_not_found',
            'cid': get_current_cid()
        }, status_code = 404)
    user_email = user_bucket.user.email if user_bucket.user is not None else None
    if is_empty(user_email):
        return JSONResponse(content = {
            'status': 'ko',
            'error': "user doesn't exists anymore",
            'i18n_code': 'user_not_found',
            'cid': get_current_cid()
        }, status_code = 404)

    try:
        bt.add_task(delete_bucket, user_bucket.provider, user_bucket, user_email)
        Bucket.updateStatus(user_bucket.id, "deleted", db)
        return JSONResponse(content = {
            'status': 'ok',
            'message': 'bucket successfully deleted',
            'i18n_code': 'bucket_deleted'
        }, status_code = 200)
    except HTTPError as e:
        return JSONResponse(content = {
            'status': 'ko',
            'error': e.msg,
            'i18n_code': e.headers["i18n_code"],
            'cid': get_current_cid()
        }, status_code = e.code)

def update_bucket(current_user, provider, region, bucket_id, db):
    if not exist_provider(provider):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'provider does not exist',
            'i18n_code': 'provider_not_exist',
            'cid': get_current_cid()
        }, status_code = 404)

    if not is_numeric(bucket_id):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Invalid bucket id',
            'i18n_code': 'invalid_payment_method_id',
            'cid': get_current_cid()
        }, status_code = 400)
    from entities.Bucket import Bucket
    user_bucket = Bucket.findUserBucket(provider, current_user.id, bucket_id, region, db)
    if not user_bucket:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'bucket not found',
            'i18n_code': '2fa_method_not_found',
            'cid': get_current_cid()
        }, status_code = 404)
    try:
        update_credentials(user_bucket.provider, user_bucket, db)
        return JSONResponse(content = {
            'status': 'ok',
            'message': 'bucket successfully updated',
            'i18n_code': 'bucket_deleted'
        }, status_code = 200)
    except HTTPError as e:
        return JSONResponse(content = {
            'status': 'ko',
            'error': e.msg,
            'i18n_code': e.headers["i18n_code"],
            'cid': get_current_cid()
        }, status_code = e.code)

def get_buckets(current_user, provider, region, db):
    if not exist_provider(provider):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'provider does not exist',
            'i18n_code': 'provider_not_exist',
            'cid': get_current_cid()
        }, status_code = 404)

    from entities.Bucket import Bucket
    userRegionBuckets = Bucket.getAllUserBucketsByRegion(provider, region, current_user.id, db)
    from entities.Access import Access
    other_buckets_access = Access.getUserAccessesByType(current_user.id, "bucket", db)
    other_buckets_ids = [access.object_id for access in other_buckets_access]
    other_buckets = Bucket.findBucketsByRegion(other_buckets_ids, provider, region, db)
    userRegionBuckets.extend(other_buckets)
    userRegionBucketsJson = json.loads(json.dumps(userRegionBuckets, cls = AlchemyEncoder))
    return JSONResponse(content = userRegionBucketsJson, status_code = 200)
