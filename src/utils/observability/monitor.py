import re
import os
import requests
import asyncio
import threading

from datetime import datetime
from time import sleep
from requests.auth import HTTPBasicAuth

from utils.common import is_empty_key, get_or_else, is_not_empty, is_not_empty_key, del_key_if_exists, sanitize_header_name, get_env_int
from utils.logger import log_msg
from utils.observability.gauge import create_gauge, set_gauge
from utils.observability.otel import get_otel_tracer
from utils.observability.traces import span_format
from utils.observability.enums import Method

URL = os.environ['DOMAIN']
VERSION = os.environ['APP_VERSION']
ENV = os.environ['APP_ENV']
MONITOR_SRC = os.getenv('MONITOR_SRC', 'cwcloud-api')
WAIT_TIME = get_env_int('WAIT_TIME', 10)

def check_status_code_pattern(actual_code, pattern):
    regexp = "^{}$".format(pattern.replace('*', '[0-9]+'))
    return bool(re.match(regexp, str(actual_code)))

def check_http_monitor(monitor, gauges):
    vdate = datetime.now()

    labels = {
        'name': monitor['name'],
        'family': monitor['family'] if is_not_empty_key(monitor, 'family') else monitor['name'],
        'source': MONITOR_SRC,
        'url': URL,
        'env': ENV,
        'version': VERSION
    }

    if monitor['type'] != 'http':
        log_msg("DEBUG", { 
            "status": "ok",
            "type": "monitor",
            "time": vdate.isoformat(),
            "message": "Not an http monitor",
            "monitor": monitor 
        })
        set_gauge(gauges['result'], 0, {**labels, 'kind': 'result', 'user': monitor['user_id']})
        return 'failure', 0

    if is_empty_key(monitor, 'url'):
        log_msg("ERROR", { 
            "status": "ko",
            "type": "monitor",
            "time": vdate.isoformat(),
            "message": "Missing mandatory url",
            "monitor": monitor 
        })
        set_gauge(gauges['result'], 0, {**labels, 'kind': 'result', 'user': monitor['user_id']})
        return

    method = get_or_else(monitor, 'method', 'GET')
    timeout = get_or_else(monitor, 'timeout', 30)
    expected_http_code = get_or_else(monitor, 'expected_http_code', '20*')
    expected_contain = get_or_else(monitor, 'expected_contain', None)
    duration = None
    auth = None
    headers = {}

    if is_not_empty_key(monitor, 'username') and is_not_empty_key(monitor, 'password'): 
        auth = HTTPBasicAuth(monitor['username'], monitor['password'])

    if is_not_empty_key(monitor, 'headers'):
        for header in monitor['headers']:
            if is_not_empty_key(header, 'name') and is_not_empty_key(header, 'value'):
                headers[sanitize_header_name(header['name'])] = header['value']

    pmonitor = monitor.copy()
    del_key_if_exists(pmonitor, 'username')
    del_key_if_exists(pmonitor, 'password')

    try:
        if method == "GET":
            response = requests.get(monitor['url'], auth=auth, headers=headers, timeout=timeout)
            duration = response.elapsed.total_seconds() * 1000
            set_gauge(gauges['duration'], duration, {**labels, 'kind': 'duration', 'user': monitor['user_id']})
        elif method == "POST":
            response = requests.post(monitor['url'], auth=auth, headers=headers, data=monitor.get('body'), timeout=timeout)
            duration = response.elapsed.total_seconds() * 1000
            set_gauge(gauges['duration'], duration, {**labels, 'kind': 'duration', 'user': monitor['user_id']})
        elif method == "PUT":
            response = requests.put(monitor['url'], auth=auth, headers=headers, data=monitor.get('body'), timeout=timeout)
            duration = response.elapsed.total_seconds() * 1000
            set_gauge(gauges['duration'], duration, {**labels, 'kind': 'duration', 'user': monitor['user_id']})
        else:
            log_msg("ERROR", { 
                "status": "ko",
                "type": "monitor",
                "time": vdate.isoformat(),
                "message": "Not supported http method: actual = {}".format(method),
                "monitor": pmonitor
            })
            set_gauge(gauges['result'], 0, {**labels, 'kind': 'result', 'user': monitor['user_id']})
            return 'failure', 0

        if not check_status_code_pattern(response.status_code, expected_http_code):
            log_msg("ERROR", { 
                "status": "ko",
                "type": "monitor",
                "time": vdate.isoformat(),
                "duration": duration,
                "message": "Not expected status code: expected pattern = {}, actual = {}".format(expected_http_code, response.status_code),
                "monitor": pmonitor
            })
            set_gauge(gauges['result'], 0, {**labels, 'kind': 'result', 'user': monitor['user_id']})
            return 'failure', duration

        if is_not_empty(expected_contain) and expected_contain not in response.text:
            log_msg("ERROR", { 
                "status": "ko",
                "type": "monitor",
                "time": vdate.isoformat(),
                "duration": duration,
                "message": "Response not valid: expected = {}, actual = {}".format(expected_contain, response.text),
                "monitor": pmonitor
            })
            set_gauge(gauges['result'], 0, {**labels, 'kind': 'result', 'user': monitor['user_id']})
            return 'failure', duration

        set_gauge(gauges['result'], 1, {**labels, 'kind': 'result', 'user': monitor['user_id']})
        log_msg("INFO", { 
            "status": "ok",
            "type": "monitor",
            "time": vdate.isoformat(),
            "duration": duration,
            "message": "Monitor is healthy",
            "monitor": pmonitor
        })
        return 'success', duration

    except Exception as e:
        set_gauge(gauges['result'], 0, {**labels, 'kind': 'result', 'user': monitor['user_id']})
        log_msg("ERROR", {
            "status": "ko",
            "type": "monitor",
            "time": vdate.isoformat(),
            "message": "Unexpected error",
            "error": "{}".format(e),
            "monitor": pmonitor
        })
        return 'failure', 0

gauges = {}

def check_monitors():
    try:
        from database.postgres_db import SessionLocal
        from entities.Monitor import Monitor

        db = SessionLocal()
        loaded_data = Monitor.getAllMonitors(db)
        labels = ['name', 'family', 'kind', 'env', 'source', 'url', 'version', 'user']

        for monitor in loaded_data:
            if monitor.name not in gauges:
                gauges[monitor.name] = {
                    'result': create_gauge(f"monitor_{monitor.name}_result", f"monitor {monitor.name} result", labels),
                    'duration': create_gauge(f"monitor_{monitor.name}_duration", f"monitor {monitor.name} duration", labels)
                }

        for monitor in loaded_data:
            monitor_dict = {
                'name': monitor.name,
                'family': monitor.family,
                'type': monitor.type,
                'url': monitor.url,
                'method': monitor.method,
                'timeout': monitor.timeout,
                'expected_http_code': monitor.expected_http_code,
                'body': monitor.body,
                'expected_contain': monitor.expected_contain,
                'username': monitor.username,
                'password': monitor.password,
                'user_id': monitor.user_id,
                'headers': [{'name': h['name'], 'value': h['value']} for h in monitor.headers] if monitor.headers else []
            }
            status, response_time = check_http_monitor(monitor_dict, gauges[monitor.name])
            Monitor.updateMonitorStatus(monitor.id, status, f'{response_time} ms', db)

    except Exception as e:
        log_msg("ERROR", {
            "status": "ko",
            "i18n_code": "monitor_check_failed",
            "type": "monitor",
            "time": datetime.now().isoformat(),
            "message": f"Error in monitor loop: {str(e)}"
        })
    finally:
        db.close()

def monitors():
    def loop_monitors():
        while True:
            with get_otel_tracer().start_as_current_span(span_format("monitors", Method.ASYNCWORKER)):
                check_monitors()
                sleep(WAIT_TIME)

    def start_monitors():
        sleep(WAIT_TIME)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(loop_monitors())

    async_thread = threading.Thread(target=start_monitors, daemon=True)
    async_thread.start()
