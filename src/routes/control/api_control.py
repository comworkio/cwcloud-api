from urllib.error import HTTPError
from fastapi import Depends, APIRouter, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database.postgres_db import get_db
from schemas.Control import ControlDeleteInstanceSchema, ControlUpdateInstanceSchema

from utils.client_ips import get_client_ips
from utils.common import is_not_empty
from utils.gitlab import delete_runner, get_project_runners
from utils import instance
from utils.logger import log_msg
from utils.observability.otel import get_otel_tracer

router = APIRouter()

_span_prefix = "control"

@router.post("/instance/{instance_id}")
def delete_instance(request: Request, bt: BackgroundTasks, instance_id: str, payload: ControlDeleteInstanceSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-delete".format(_span_prefix)):
        error = payload.error
        from entities.Instance import Instance
        userInstance = Instance.findInstanceById(instance_id, db)
        if not userInstance:
            return JSONResponse(content = {"error": f"No server found with this name"}, status_code = 404)

        client_ips = get_client_ips(request)
        instance_ip = userInstance.ip_address
        if not any(is_not_empty(ip) and ip == instance_ip for ip in client_ips):
            log_msg("ERROR", "[api_control] post instance 403: not the expected instance_ip = {} not in client_ips = {}".format(instance_ip, client_ips))
            return JSONResponse(content = {"error": f"Access denied for this ip address"}, status_code = 403)

        server = instance.get_virtual_machine(userInstance.provider, userInstance.region, userInstance.zone, f"{userInstance.name}-{userInstance.hash}")

        if not server:
            return JSONResponse(content = {"error": f"No server found with this name"}, status_code = 404)

        server_state = server["state"]

        if not server_state == "running" and not server_state == "stopped":
            return JSONResponse(content = {"error": f"You can\"t delete the instance while it is {server_state}"}, status_code = 404)

        try:
            bt.add_task(instance.delete_instance, userInstance.hash, userInstance.name, userInstance.user.email)
            runners = get_project_runners(userInstance.project.id, userInstance.project.gitlab_host, userInstance.project.access_token)
            filtered_runners = [runner for runner in runners if runner["ip_address"] == userInstance.ip_address]
            if len(filtered_runners) > 0:
                delete_runner(filtered_runners[0]["id"], userInstance.project.gitlab_host, userInstance.project.access_token)
            Instance.updateStatus(userInstance.id, "deleted", db)
            log_msg("ERROR", f"[cloud-init] Cloud init failed for instance # {instance_id} processing to deletion.")
            log_msg("ERROR", f"[cloud-init] {error}")

            return JSONResponse(content = {"message": "instance successfully deleted", "i18n_code": "102"}, status_code = 200)
        except HTTPError as e:
            return JSONResponse(content = {"error": e.msg, "i18n_code": e.headers["i18n_code"]}, status_code = e.code)

@router.patch("/instance/{instance_id}")
def update_instance(request: Request, instance_id: str, payload: ControlUpdateInstanceSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-patch".format(_span_prefix)):
        action = payload.status
        from entities.Instance import Instance
        userInstance = Instance.findInstanceById(instance_id, db)
        if not userInstance:
            return JSONResponse(content = {"error": f"No server found with this name"}, status_code = 404)

        client_ips = get_client_ips(request)
        instance_ip = userInstance.ip_address
        if not any(is_not_empty(ip) and ip == instance_ip for ip in client_ips):
            log_msg("ERROR", "[api_control] patch instance 403: not the expected instance_ip = {} not in client_ips = {}".format(instance_ip, client_ips))
            return JSONResponse(content = {"error": f"Access denied for this ip address"}, status_code = 403)

        server = instance.get_virtual_machine(userInstance.provider, userInstance.region, userInstance.zone, f"{userInstance.name}-{userInstance.hash}")

        if not server:
            return JSONResponse(content = {"error": f"No server found with this name"}, status_code = 404)

        target_server_id = server["id"]

        if not action  == "activate":
            return JSONResponse(content = {"error": f"This action doesnt exist"}, status_code = 400)

        try:
            if userInstance.status == "active" and action == "activate":
                return JSONResponse(content = {"error": "instance already active"}, status_code = 400)
            instance.update_instance_status(userInstance, target_server_id, action, db)
            return JSONResponse(content = {"message": "instance successfully updated", "i18n_code": "101"}, status_code = 200)
        except HTTPError as e:
            return JSONResponse(content = {"error": e.msg, "i18n_code": e.headers["i18n_code"]}, status_code = e.code)
