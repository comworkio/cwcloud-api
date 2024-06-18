from middleware.k8sapi_guard import k8sapi_required
from middleware.daasapi_guard import daasapi_required

def check_permissions(current_user, type, db):
    if type == "vm":
        daasapi_required(current_user, db)
    elif type == "k8s":
        k8sapi_required(current_user, db)
    elif type == "all":
        daasapi_required(current_user, db)
        k8sapi_required(current_user, db)
