from middleware.k8sapi_guard import k8sapi_required
from middleware.daasapi_guard import daasapi_required
from utils.common import is_true

def check_permissions(current_user, type, db):
    if is_true(current_user.is_admin):
        return
    if type == "vm":
        daasapi_required(current_user, db)
    elif type == "k8s":
        k8sapi_required(current_user, db)
    elif type == "all":
        daasapi_required(current_user, db)
        k8sapi_required(current_user, db)
