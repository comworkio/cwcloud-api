import os
import requests

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from utils.common import is_empty_key, is_not_empty
from utils.cron import parse_crontab
from utils.logger import log_msg

global _scheduler
_scheduler = BackgroundScheduler()
_scheduler.start()

_api_endpoint = "{}/v1/faas".format(os.environ['FAAS_API_URL'])
_api_admin_endpoint = "{}/v1/admin/faas".format(os.environ['FAAS_API_URL'])
_api_token = os.getenv('FAAS_API_TOKEN')
_headers = { "X-Auth-Token": _api_token } if is_not_empty(_api_token) else None
_max_results = int(os.environ['API_MAX_RESULTS'])

def invoke_function(trigger):
    invocation_endpoint = "{}/invocation"
    log_msg("DEBUG", "[scheduler][invoke_function] invoke trigger: {}, invocation_endpoint = {}/invocation".format(trigger, invocation_endpoint))
    requests.post(invocation_endpoint.format(_api_endpoint), json = {
        'content': {
            'invoker_id': trigger['owner']['id'],
            'function_id': trigger['content']['function_id'],
            'args': trigger['content']['args']
        }
    }, headers = _headers)

def reinit_crontabs():
    global _scheduler
    _scheduler.shutdown(wait = False)
    _scheduler = BackgroundScheduler()
    _scheduler.start()

    start_index = 0
    while True:
        trigger_endpoint = "{}/triggers".format(_api_admin_endpoint)
        log_msg("DEBUG", "[scheduler][reinit_crontabs] trigger_endpoint = {}".format(trigger_endpoint))
        r_triggers = requests.get("{}?start_index={}&max_results={}&kind=cron".format(trigger_endpoint, start_index, _max_results), headers = _headers)
        if r_triggers.status_code != 200:
            log_msg("ERROR", "[scheduler][reinit_crontabs] triggers api respond an error, r.code = {}, r.body = {}".format(r_triggers.status_code, r_triggers))    
            return

        triggers = r_triggers.json()
        if is_empty_key(triggers, 'results'):
            log_msg("DEBUG", "[scheduler][reinit_crontabs] no more triggers found...")    
            break

        for trigger in triggers['results']:
            if is_empty_key(trigger, 'content') or any(is_empty_key(trigger['content'], k) for k in ['cron_expr', 'name', 'function_id']):
                log_msg("WARN", "[scheduler][reinit_crontabs] missing some mandatory fields, ignoring trigger = {}".format(trigger))
                continue

            if not 'args' in trigger['content']:
                log_msg("WARN", "[scheduler][reinit_crontabs] missing args mandatory fields, ignoring trigger = {}".format(trigger))
                continue

            apscheduler_args = parse_crontab(trigger['content']['cron_expr'])
            log_msg("DEBUG", "[scheduler][reinit_crontabs] add this cron: name = {}, cron_expr = {}, apscheduler_args = {}".format(trigger['content']['name'], trigger['content']['cron_expr'], apscheduler_args))
            _scheduler.add_job(lambda: invoke_function(trigger), CronTrigger(**apscheduler_args), id = trigger['content']['name'])
        start_index = start_index + 1
