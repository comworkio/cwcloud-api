import json

from urllib.error import HTTPError
from pulumi import automation as auto
from fastapi import BackgroundTasks
from fastapi.responses import JSONResponse

from entities.Bucket import Bucket
from entities.User import User

from utils.bucket import create_bucket, delete_bucket, refresh_bucket, register_bucket, update_credentials
from utils.common import is_empty, is_not_empty, is_numeric, is_true
from utils.instance import check_instance_name_validity
from utils.bytes_generator import generate_hashed_name
from utils.provider import exist_provider, get_provider_infos
from utils.encoder import AlchemyEncoder
from utils.observability.cid import get_current_cid

def admin_create_bucket(current_user, provider, region, payload, db, bt: BackgroundTasks):
    bucket_name = payload.name
    email = payload.email
    bucket_type = payload.type

    try:
        if not exist_provider(provider):
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'provider does not exist', 
                'i18n_code': '504',
                'cid': get_current_cid()
            }, status_code = 404)

        if is_empty(bucket_name):
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'please provide bucket name', 
                'i18n_code': '1101',
                'cid': get_current_cid()
            }, status_code = 400)

        if is_empty(email):
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'please provide an email', 
                'i18n_code': '1102',
                'cid': get_current_cid()
            }, status_code = 400)

        if is_empty(bucket_type):
            bucket_type = get_provider_infos(provider, "bucket_types")[0]
        else:
            possible_types = get_provider_infos(provider, "bucket_types")
            if bucket_type not in possible_types:
                return JSONResponse(content = {
                    'status': 'ko',
                    'error': 'bucket type does not exist', 
                    'i18n_code': '1103',
                    'cid': get_current_cid()
                }, status_code = 400)

        possible_regions = get_provider_infos(provider, "bucket_available_regions")
        if region not in possible_regions:
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'region does not exist', 
                'i18n_code': '1104',
                'cid': get_current_cid()
            }, status_code = 400)

        exist_user = User.getUserByEmail(email, db)
        chosen_user_id = exist_user.id
        if not exist_user:
            return JSONResponse(content = {
                'status': 'ko',
                'error': 'user not found', 
                'i18n_code': '304',
                'cid': get_current_cid()
            }, status_code = 404)

        check_instance_name_validity(bucket_name)
        hash, hashed_bucket_name = generate_hashed_name(bucket_name)
        new_bucket = register_bucket(hash, provider, region, chosen_user_id, current_user.id, bucket_name, bucket_type, db)

        bt.add_task(create_bucket, provider, exist_user.email, new_bucket.id, hashed_bucket_name, region, bucket_type, db)

        new_bucket_json = json.loads(json.dumps(new_bucket, cls = AlchemyEncoder))
        return JSONResponse(content = new_bucket_json, status_code = 200)
    except auto.StackAlreadyExistsError:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'stack already exists', 
            'i18n_code': '1105',
            'cid': get_current_cid()
        }, status_code = 409)
    except HTTPError as e:
        return JSONResponse(content = {
            'status': 'ko',
            'error': "{}".format(e),
            'cid': get_current_cid()
        }, status_code = e.code)
    except Exception as exn:
        return JSONResponse(content = {
            'status': 'ko',
            'error': "{}".format(exn),
            'cid': get_current_cid()
        }, status_code = 500)
def admin_get_bucket(current_user, bucket_id, db):
    if not is_numeric(bucket_id):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Invalid bucket id',
            'cid': get_current_cid()
        }, status_code = 400)
    userBucket = Bucket.findById(bucket_id, db)
    if not userBucket:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Bucket not found', 
            'i18n_code': 'status_code = 404',
            'cid': get_current_cid()
        }, status_code = 404)
    dumpedBucket = json.loads(json.dumps(userBucket, cls = AlchemyEncoder))
    dumpedUser = json.loads(json.dumps(userBucket.user, cls = AlchemyEncoder))
    bucketJson = {**dumpedBucket, "user": {**dumpedUser}}
    return JSONResponse(content = bucketJson, status_code = 200)

def admin_remove_bucket(current_user, bucket_id, db, bt: BackgroundTasks):
    if not is_numeric(bucket_id):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Invalid bucket id',
            'cid': get_current_cid()
        }, status_code = 400)

    user_bucket = Bucket.findById(bucket_id, db)
    if not user_bucket:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'bucket not found', 
            'i18n_code': '404',
            'cid': get_current_cid()
        }, status_code = 404)

    user_id = user_bucket.user_id
    user = User.getUserById(user_id, db) if is_not_empty(user_id) else None
    user_email = user.email if user is not None else None

    if is_empty(user_email):
        Bucket.updateStatus(user_bucket.id, 'deleted', db)
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
            'i18n_code': '401'
        }, status_code = 200)
    except HTTPError as e:
        return JSONResponse(content = {
            'status': 'ko',
            'error': e.msg, 
            'i18n_code': e.headers['i18n_code'],
            'cid': get_current_cid()
        }, status_code = e.code)

def admin_refresh_bucket(current_user, bucket_id, db):
    if not is_numeric(bucket_id):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Invalid bucket id',
            'cid': get_current_cid()
        }, status_code = 400)

    userBucket = Bucket.findById(bucket_id, db)
    if not userBucket:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Bucket not found', 
            'i18n_code': '104',
            'cid': get_current_cid()
        }, status_code = 404)

    hashed_bucket_name = f"{userBucket.name}-{userBucket.hash}"

    try:
        refresh_bucket(current_user.email, userBucket.provider, userBucket.id, hashed_bucket_name, db)
        return JSONResponse(content = {
            'status': 'ok',
            'message': 'bucket successfully refreshed', 
            'i18n_code': '405'
        }, status_code = 200)
    except HTTPError as e:
        return JSONResponse(content = {
            'status': 'ko',
            'error': e.msg, 
            'i18n_code': e.headers['i18n_code'],
            'cid': get_current_cid()
        }, status_code = e.code)

def admin_update_bucket(current_user, bucket_id, payload, db):
    if not is_numeric(bucket_id):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'Invalid bucket id',
            'cid': get_current_cid()
        }, status_code = 400)

    existing_bucket = Bucket.findById(bucket_id, db)
    if not existing_bucket:
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'bucket not found', 
            'i18n_code': '404',
            'cid': get_current_cid()
        }, status_code = 404)

    try:
        email = None
        update_creds = False
        if is_not_empty(payload):
            email = payload.email
            update_creds = payload.update_creds

        if is_true(update_creds):
            update_credentials(existing_bucket.provider, existing_bucket, existing_bucket.user.email, db)

        if is_not_empty(email):
            from entities.User import User
            user = User.getUserByEmail(email, db)
            if not user:
                return JSONResponse(content = {
                    'status': 'ko',
                    'error': 'user not found', 
                    'i18n_code': '304',
                    'cid': get_current_cid()
                }, status_code = 404)
            Bucket.patch(bucket_id, {"user_id": user.id}, db)
        return JSONResponse(content = {
            'status': 'ok',
            'message': 'bucket successfully updated', 
            'i18n_code': '402'
        }, status_code = 200)
    except HTTPError as e:
        return JSONResponse(content = {
            'status': 'ko',
            'error': e.msg, 
            'i18n_code': e.headers['i18n_code'],
            'cid': get_current_cid()
        }, status_code = e.code)

def admin_get_buckets(current_user, provider, region, db):
    if not exist_provider(provider):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'provider does not exist', 
            'i18n_code': '504',
            'cid': get_current_cid()
        }, status_code = 404)

    userRegionBuckets = Bucket.getAllBucketsByRegion(provider, region, db)
    userRegionBucketsJson = json.loads(json.dumps(userRegionBuckets, cls = AlchemyEncoder))
    return JSONResponse(content = userRegionBucketsJson, status_code = 200,)

def admin_get_user_buckets(current_user, provider, region, user_id, db):
    if not exist_provider(provider):
        return JSONResponse(content = {
            'status': 'ko',
            'error': 'provider does not exist', 
            'i18n_code': '504',
            'cid': get_current_cid()
        }, status_code = 404)

    userRegionBuckets = Bucket.getAllUserBucketsByRegion(provider, region, user_id, db)
    userRegionBucketsJson = json.loads(json.dumps(userRegionBuckets, cls = AlchemyEncoder))
    return JSONResponse(content = userRegionBucketsJson, status_code = 200)
