import os
import json

from datetime import datetime, timedelta
from urllib.error import HTTPError
from jose.exceptions import ExpiredSignatureError, JOSEError, JWTError

from fastapi import HTTPException
from fastapi.responses import JSONResponse

from entities.User import User

from utils.common import generate_hash_password, is_boolean, is_empty, is_false, is_true, verify_password
from utils.encoder import AlchemyEncoder
from utils.jwt import jwt_decode, jwt_encode
from utils.logger import log_msg
from utils.payment import PAYMENT_ADAPTER
from utils.mail import send_confirmation_email, send_forget_password_email
from utils.gitlab import create_gitlab_user
from utils.security import check_password, is_not_email_valid

def get_current_user_data(current_user, db):
    user = User.getUserById(current_user.id, db)
    if is_empty(user):
        return JSONResponse(content = {"error": "user not found", "i18n_code": "304"}, status_code = 404)
    return user

def update_user_informations(current_user, payload, db):
    email = payload.email
    if is_not_email_valid(email):
        return JSONResponse(content = {"error": "email is not valid", "i18n_code": "not_valid_email"}, status_code = 400)

    user = User.getUserById(current_user.id, db)
    if user and int(user.id) != int(current_user.id) :
        return JSONResponse(content = {"error": f"email already exists", "i18n_code": "305"}, status_code = 409)

    User.updateUser(current_user.id, payload, db)
    return JSONResponse(content = {"message": f"user successfully updated", "i18n_code": "301"}, status_code = 200)

def create_customer(email):
    return PAYMENT_ADAPTER().create_customer(email)

def create_user_account(payload, db):
    try:
        email = payload.email
        password = payload.password

        if is_not_email_valid(email):
            return JSONResponse(content = {"error": "email is not valid", "i18n_code": "not_valid_email"}, status_code = 400)

        check = check_password(password)
        if is_false(check["status"]):
            return JSONResponse(content ={"error": "the password is invalid", "i18n_code": check["i18n_code"]}, status_code = 400)

        exist_user = User.getUserByEmail(email, db)
        if exist_user:
            return JSONResponse(content = {"error": "email already exists", "i18n_code": "305"}, status_code = 409)

        customer = create_customer(email)
        payload.password = generate_hash_password(password)
        new_user = User(**payload.dict())
        new_user.st_customer_id = customer["id"]
        new_user.save(db)
        create_gitlab_user(email)
        subject = "Confirm your account"
        token = jwt_encode({
            "exp": (datetime.now() + timedelta(minutes = 5)).timestamp(),
            "id": new_user.id,
            "email": new_user.email,
            "time": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        })
        activation_link = "{}/confirmation/{}".format(os.getenv("DOMAIN"), token)
        log_msg("INFO", f"[api_user_signup] User {email} has joined comwork cloud")
        log_msg("INFO", f"[api_user_signup] Sending confirmation email to {email}")
        send_confirmation_email(new_user.email, activation_link, subject)
        return JSONResponse(content = {"status": "ok", "message": "user successfully created", "id": new_user.id, "i18n_code": "300"}, status_code = 201)
    except HTTPException as e:
        return JSONResponse(content = {"error": e.msg, "i18n_code": e.headers["i18n_code"]}, status_code = e.code)

def get_user_cloud_statistics(current_user, db):
    from entities.Instance import Instance
    from entities.Access import Access
    from entities.Project import Project
    from entities.Bucket import Bucket
    from entities.Registry import Registry
    instances = len(Instance.getActiveUserInstances(current_user.id, db))
    instances = instances + len(Access.getUserAccessesByType(current_user.id, "instance", db))
    projects = len(Project.getUserProjects(current_user.id, db))
    projects = projects + len(Access.getUserAccessesByType(current_user.id, "project", db))
    buckets = len(Bucket.getAllUserBuckets(current_user.id, db))
    buckets = buckets + len(Access.getUserAccessesByType(current_user.id, "bucket", db))
    registries = len(Registry.getAllUserRegistries(current_user.id, db))
    registries = registries + len(Access.getUserAccessesByType(current_user.id, "registry", db))

    return JSONResponse(content = {"projects": projects, "instances": instances, "buckets": buckets, "registries": registries}, status_code = 200)

def update_user_autopayment(current_user, payload, db):
    status = payload.status
    if not is_boolean(status):
        return JSONResponse(content = {"error": "missing argument status"}, status_code = 400)

    from entities.User import User
    user = User.getUserById(current_user.id, db)
    if is_empty(user.st_payment_method_id):
        return JSONResponse(content = {"error": "default payment method must be selected", "i18n_code": "1300"}, status_code = 400)

    User.updateUserAutoPayment(current_user.id, is_true(status), db)
    return JSONResponse(content = {"message": "successfully updated auto payment status"}, status_code = 200)

def get_user_cloud_resources(current_user, db):
    from entities.Instance import Instance
    instances = Instance.getActiveUserInstances(current_user.id, db)
    instancesJson = json.loads(json.dumps(instances, cls = AlchemyEncoder))

    from entities.Project import Project
    projects = Project.getUserProjects(current_user.id, db)
    projectsJson = json.loads(json.dumps(projects, cls = AlchemyEncoder))

    from entities.Bucket import Bucket
    buckets = Bucket.getAllUserBuckets(current_user.id, db)
    bucketsJson = json.loads(json.dumps(buckets, cls = AlchemyEncoder))

    from entities.Registry import Registry
    registries = Registry.getAllUserRegistries(current_user.id, db)
    registriesJson = json.loads(json.dumps(registries, cls = AlchemyEncoder))

    return JSONResponse(content = {"projects": projectsJson, "instances": instancesJson, "buckets": bucketsJson, "registries": registriesJson}, status_code = 200)

def update_user_password(current_user, payload, db):
    new_password = payload.new_password
    check = check_password(new_password)
    if is_false(check["status"]):
        return JSONResponse(content = {"error": "the password is invalid", "i18n_code": check["i18n_code"]}, status_code = 400)

    user = User.getUserById(current_user.id, db)
    if not user:
        return JSONResponse(content = {"error": "user not found", "i18n_code": "304"}, status_code = 409)

    if not verify_password(payload.old_password, user.password):
        return JSONResponse(content = {"error": "wrong password", "i18n_code": "311"}, status_code = 409)

    User.updateUserPassword(user.id, new_password, db)
    return JSONResponse(content = {"message": f"user successfully updated", "i18n_code": "301"}, status_code = 200)

def forget_password_email(payload, db):
    try:
        email = payload.email
        if is_not_email_valid(email):
            return JSONResponse(content = {"error": "invalid email", "i18n_code": "not_valid_email"}, status_code = 400)

        user = User.getUserByEmail(email, db)
        if not user:
            return JSONResponse(content = {"error": "user not found", "i18n_code": "304"}, status_code = 409)

        subject = "Forgotten password"
        token = jwt_encode({
            "exp": (datetime.now() + timedelta(minutes = 5)).timestamp(),
            "id": user.id,
            "email": user.email,
            "time": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        })
        activation_link = "{}/reset-password/{}".format(os.getenv("DOMAIN"), token)
        send_forget_password_email(user.email, activation_link, subject)
        log_msg("INFO", f"[api_reset_password] User {user.email} requested a reset password email")
        return JSONResponse(content = {"status": "ok", "message": "successfully sent reset password email", "i18n_code": "309"}, status_code = 200)
    except HTTPException as e:
        return JSONResponse(content = {"error": e.msg, "i18n_code": e.headers["i18n_code"]}, status_code = e.code)

def user_reset_password(payload, db):
    try:
        email = payload.email
        password = payload.password
        if is_not_email_valid(email):
            return JSONResponse(content = {"error": "invalid email", "i18n_code": "not_valid_email"}, status_code = 400)
        check = check_password(password)
        if is_false(check["status"]):
            return JSONResponse(content = {"error": "the password is invalid", "i18n_code": check["i18n_code"]}, status_code = 400)

        user = User.getUserByEmail(email, db)
        if not user:
            return JSONResponse(content = {"error": "user not found", "i18n_code": "304"}, status_code = 409)

        User.updateUserPasswordAndConfirm(user.id, password, db)
        return JSONResponse(content = {"status": "ok", "message": "user successfully updated", "i18n_code": "301"}, status_code = 200)
    except HTTPException as e:
        return JSONResponse(content = {"error": e.msg, "i18n_code": e.headers["i18n_code"]}, status_code = e.code)

def verify_user_token(token, db):
    if is_empty(token):
        return JSONResponse(content = {"error": "a confirmation token is mandatory", "i18n_code": "312"}, status_code = 400)
    try:
        data = jwt_decode(token)
        user = User.getUserByEmail(data["email"], db)
        if not user:
            return JSONResponse(content = {"error": "user not found", "i18n_code": "304"}, status_code = 404)
        return JSONResponse(content = {"email": user.email, "message": "user verified", "i18n_code": "307"}, status_code = 200)
    except HTTPException as e:
        return JSONResponse(content = {"error": e.msg, "i18n_code": e.headers["i18n_code"]}, status_code = e.code)
    except ExpiredSignatureError as e:
        log_msg("WARN", "[user][verify_user_token] expired signature: e.type = {}, e.msg = {}".format(type(e), e))
        return JSONResponse(content = {"error": "user verification failed", "i18n_code": "308"}, status_code = 400)
    except JOSEError as e:
        log_msg("WARN", "[user][verify_user_token] invalid jwt token: e.type = {}, e.msg = {}".format(type(e), e))
        return JSONResponse(content = {"error": "invalid jwt token", "i18n_code": "313"}, status_code = 400)
    except Exception as e:
        log_msg("ERROR", "[user][verify_user_token] err :{}".format(e))
        return JSONResponse(content = {"error": "technical error", "i18n_code": "314"}, status_code = 500)

def confirm_user_account(token, db):
    if is_empty(token):
        return JSONResponse(content = {"error": "a confirmation token is mandatory", "i18n_code": "312"}, status_code = 400)
    try:
        data = jwt_decode(token)
        user = User.getUserByEmail(data["email"], db)
        if not user:
            return JSONResponse(content = {"error": "user not found", "i18n_code": "304"}, status_code = 404)
        if user.confirmed:
            return JSONResponse(content = {"error": "user already confirmed", "i18n_code": "310"}, status_code = 409)
        User.updateConfirmation(user.id, True, db)
        return JSONResponse(content = {"email": user.email, "message": "user successfully confirmed", "i18n_code": "303"}, status_code = 200)
    except HTTPException as e:
        return JSONResponse(content = {"error": e.msg, "i18n_code": e.headers["i18n_code"]}, status_code = e.code)
    except JWTError as e:
        log_msg("WARN", "[user][confirm_user_account] invalid jwt token :{}".format(e))
        return JSONResponse(content = {"error": "invalid jwt token", "i18n_code": "313"}, status_code = 400)
    except ExpiredSignatureError:
        return JSONResponse(content = {"error": "user verification failed", "i18n_code": "308"}, status_code = 400)
    except Exception as e:
        log_msg("ERROR", "[user][confirm_user_account] e.type = {}, e.msg = {}".format(type(e), e))
        return JSONResponse(content = {"error": "technical error", "i18n_code": "314"}, status_code = 500)

def confirmation_email(payload, db):
    try:
        email = payload.email
        if is_not_email_valid(email):
            return JSONResponse(content = {"error": "email is not valid", "i18n_code": "not_valid_email"}, status_code = 400)

        user = User.getUserByEmail(email, db)
        if not user:
            return JSONResponse(content = {"error": "user not found", "i18n_code": "304"}, status_code = 404)
        if user.confirmed:
            return JSONResponse(content = {"error": "user already confirmed", "i18n_code": "310"}, status_code = 409)

        subject = "Confirm your account"
        token = jwt_encode({
            "exp": (datetime.now() + timedelta(minutes = 5)).timestamp(),
            "id": user.id,
            "email": user.email,
            "time": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        })
        activation_link = "{}/confirmation/{}".format(os.getenv("DOMAIN"), token)
        log_msg("INFO", f"[api_confirm_account] User {user.email} requested a confirm account email")
        send_confirmation_email(user.email, activation_link, subject)
        return JSONResponse(content = {"status": "ok", "message": "successfully send email confirmation", "i18n_code": "306"}, status_code = 200)
    except HTTPError as e:
        return JSONResponse(content = {"error": e.msg, "i18n_code": e.headers["i18n_code"]}, status_code = e.code)

def listPaymentMethods(user):
    return PAYMENT_ADAPTER().list_payment_methods(user)

def get_payment_methods(current_user, db):
    from entities.User import User
    user = User.getUserById(current_user.id, db)
    return JSONResponse(content = {"payment_method": listPaymentMethods(user)}, status_code = 200)

def attachPaymentMethodWithUser(payment_method, user):
    return PAYMENT_ADAPTER().attach_payment_method(payment_method, user)

def retrievePaymentMethod(payment_method_id):
    return PAYMENT_ADAPTER().retrieve_payment_method(payment_method_id)

def add_payment_method(current_user, payload, db):
    payment_method = payload.payment_method
    if not retrievePaymentMethod(payment_method):
        return JSONResponse(content = {"error": "payment method not found", "i18n_code": "payment_method_not_found"}, status_code = 404)

    from entities.User import User
    user = User.getUserById(current_user.id, db)
    if is_empty(user.st_payment_method_id):
        User.activateUserPayment(current_user.id, payment_method, db)
    if not attachPaymentMethodWithUser(payment_method, user):
        return JSONResponse(content = {"error": "payment method not found", "i18n_code": "payment_method_not_found"}, status_code = 404)

    return JSONResponse(content = {"message": "payment method successfully added"}, status_code = 204)

def remove_payment_method(current_user, payment_method_id, db):
    if is_empty(payment_method_id):
        return JSONResponse(content = {"error": "Invalid payment method id", "i18n_code": "400"}, status_code = 400)

    payment_method = PAYMENT_ADAPTER().retrieve_payment_method(payment_method_id)
    if is_empty(payment_method):
        return JSONResponse(content = {"error": "payment method not found", "i18n_code": "payment_method_not_found"}, status_code = 404)

    from entities.User import User
    user = User.getUserById(current_user.id, db)
    if user.st_payment_method_id == payment_method_id:
        User.desactivateUserPayment(current_user.id, db)

    if not PAYMENT_ADAPTER().detach_payment_method(payment_method_id):
        return JSONResponse(content = {"error": "payment method not found", "i18n_code": ""}, status_code = 404)

    return JSONResponse(content = {"message": "payment method successfully removed"}, status_code = 204)

def update_payment_method(current_user, payment_method_id, db):
    if is_empty(retrievePaymentMethod(payment_method_id)):
        return JSONResponse(content = {"error": "payment method not found", "i18n_code": "payment_method_not_found"}, status_code = 404)

    if is_empty(payment_method_id):
        return JSONResponse(content = {"error": "Invalid payment method id", "i18n_code": "400"}, status_code = 400)

    from entities.User import User
    user = User.getUserById(current_user.id, db)
    if user.st_payment_method_id == payment_method_id:
        #? If we"re getting here, that means the user tried to unselect the selected payment method
        return JSONResponse(content = {"error": "A default payment method must be set and selected", "i18n_code": "1300"}, status_code = 400)
    if is_empty(user.st_payment_method_id):
        User.activateUserPayment(current_user.id, payment_method_id, db)

    User.setUserStripePaymentMethodId(current_user.id, payment_method_id, db)

    return JSONResponse(content = {"message": "payment method successfully updated"}, status_code = 204)
