import os
import asyncio
import threading

from time import sleep

from utils.observability.gauge import create_gauge, set_gauge
from utils.observability.otel import get_otel_tracer
from utils.observability.resources import all_metrics

_loop_wait_time = int(os.environ['LOOP_WAIT_TIME'])

cpu_gauge = create_gauge("cpu_all", "cpu usage in percent")
ram_total_gauge = create_gauge("ram_total", "total of ram")
ram_available_gauge = create_gauge("ram_available", "available ram")
ram_percent_gauge = create_gauge("ram_percent", "percent ram")
disk_free_gauge = create_gauge("disk_free", "free storage's space")
disk_used_gauge = create_gauge("disk_used", "used storage's space")
disk_percent_gauge = create_gauge("disk_percent", "percent storage's space")
disk_total_gauge = create_gauge("disk_total", "total storage's space")
swap_free_gauge = create_gauge("swap_free", "free swap")
swap_used_gauge = create_gauge("swap_used", "used swap")
swap_total_gauge = create_gauge("swap_total", "total swap")
swap_percent_gauge = create_gauge("swap_percent", "percent swap")

def cpu(metrics):
    cpu_usage_percent = metrics['cpu']['percent']['all']
    set_gauge(cpu_gauge, cpu_usage_percent)

def ram(metrics):
    memory_usage_percent = metrics['virtual_memory']['percent']
    set_gauge(ram_total_gauge, metrics['virtual_memory']['total'])
    set_gauge(ram_available_gauge, metrics['virtual_memory']['available'])
    set_gauge(ram_percent_gauge, memory_usage_percent)

def swap(metrics):
    swap_usage_percent = metrics['swap_memory']['percent']
    set_gauge(swap_free_gauge, metrics['swap_memory']['free'])
    set_gauge(swap_used_gauge, metrics['swap_memory']['used'])
    set_gauge(swap_total_gauge, metrics['swap_memory']['total'])
    set_gauge(swap_percent_gauge, swap_usage_percent)

def disc(metrics):
    disc_usage_percent = metrics['disk_usage']['percent']
    set_gauge(disk_free_gauge, metrics['disk_usage']['free'])
    set_gauge(disk_used_gauge, metrics['disk_usage']['used'])
    set_gauge(disk_total_gauge, metrics['disk_usage']['total'])
    set_gauge(disk_percent_gauge, disc_usage_percent)

_span_prefix = "metrics"

def metrics():
    def loop_metrics():
        while True:
            with get_otel_tracer().start_as_current_span("{}-loop".format(_span_prefix)):
                metrics = all_metrics()
                cpu(metrics)
                ram(metrics)
                swap(metrics)
                disc(metrics)
                sleep(_loop_wait_time)

    def start_metrics():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(loop_metrics())

    async_thread = threading.Thread(target=start_metrics, daemon=True)
    async_thread.start()
