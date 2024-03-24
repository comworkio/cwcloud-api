import os
import importlib
import requests
import pulumi
import lbrlabs_pulumi_scaleway as scaleway

from pulumi import automation as auto, ResourceOptions
from urllib.error import HTTPError

from drivers.ProviderDriver import ProviderDriver

from utils.common import is_not_empty, is_true
from utils.dns_zones import get_dns_zone_driver, register_scaleway_domain
from utils.list import unmarshall_list_array
from utils.driver import sanitize_project_name, convert_instance_state
from utils.logger import log_msg

SCW_API_URL = "https://api.scaleway.com"

class ScalewayDriver(ProviderDriver):
    def create_dns_records(self, record_name, environment, ip_address, root_dns_zone):
        sw_api_key = os.getenv('SCW_SECRET_KEY')
        project_id = os.getenv('SCW_PROJECT_ID')
        dnsZonesResponse = requests.get(f'{SCW_API_URL}/domain/v2beta1/domains/{root_dns_zone}/dns-zones', headers = {"X-Auth-Token": sw_api_key})
        dnsZones = dnsZonesResponse.json()["dns_zones"]
        availableZones = []
        for zone in dnsZones:
            availableZones.append(zone['subdomain'])

        if not environment['path'] in availableZones:
            newDnsInfo = {
                "domain": root_dns_zone,
                "subdomain": environment['path'],
                "project_id": project_id
            }
            dnsZones = requests.post(f'{SCW_API_URL}/domain/v2beta1/dns-zones', headers = {"X-Auth-Token": sw_api_key}, json = newDnsInfo)

        register_scaleway_domain(record_name, environment['path'], ip_address, root_dns_zone)
        for subdomain in unmarshall_list_array(environment['subdomains']):
            dns_record_name = "{}.{}".format(subdomain, record_name)
            register_scaleway_domain(dns_record_name, environment['path'], ip_address, root_dns_zone)

    def create_instance(self, instance_id, ami_image, hashed_instance_name, environment, instance_region, instance_zone, instance_type, generate_dns, root_dns_zone):
        def create_pulumi_program():
            region_zone = "{}-{}".format(instance_region, instance_zone)
            instance_ip = scaleway.InstanceIp("publicIp", zone = region_zone)
            new_instance = scaleway.InstanceServer(hashed_instance_name,
                                    type = instance_type,
                                    image = ami_image,
                                    name = hashed_instance_name,
                                    ip_id = instance_ip.id,
                                    zone = region_zone,
                                    user_data = {
                                        "cloud-init": (lambda path: open(path).read())(self.cloud_init_script())
                                    })

            if is_true(generate_dns):
                dns_driver = get_dns_zone_driver(root_dns_zone)
                ProviderDriverModule = importlib.import_module('drivers.{}'.format(dns_driver))
                ProviderDriver = getattr(ProviderDriverModule, dns_driver)
                ProviderDriver().create_dns_records(hashed_instance_name, environment, new_instance.public_ip, root_dns_zone)
            pulumi.export("public_ip", new_instance.public_ip)

        scw_access_key = os.getenv('SCW_ACCESS_KEY')
        scw_secret_key = os.getenv('SCW_SECRET_KEY')
        scw_project_id = os.getenv('SCW_PROJECT_ID')
        cloudflare_api_token = os.getenv('CLOUDFLARE_API_TOKEN')

        stack = auto.create_or_select_stack(stack_name = hashed_instance_name,
                                            project_name = sanitize_project_name(environment['path']),
                                            program = create_pulumi_program)
        stack.set_config("scaleway:access_key", auto.ConfigValue(scw_access_key))
        stack.set_config("scaleway:secret_key", auto.ConfigValue(scw_secret_key))
        stack.set_config("scaleway:project_id", auto.ConfigValue(scw_project_id))
        if is_not_empty(cloudflare_api_token):
            stack.set_config("cloudflare:api_token", auto.ConfigValue(cloudflare_api_token))
        up_res = stack.up()

        return {
            "ip": up_res.outputs.get("public_ip").value
        }

    def refresh_instance(self, instance_id, hashed_instance_name, environment, instance_region, instance_zone):
        def create_pulumi_program():
            region_zone = "{}-{}".format(instance_region, instance_zone)
            existing_instance = scaleway.get_instance_server(hashed_instance_name)
            existingInstanceIp = scaleway.get_instance_ip(existing_instance.public_ip)
            scaleway.InstanceIp("publicIp", opts = ResourceOptions(import_ = existingInstanceIp.id))
            scaleway.InstanceServer(hashed_instance_name,
                                    image = existing_instance.image,
                                    name = hashed_instance_name,
                                    type = existing_instance.type,
                                    zone = region_zone,
                                    ip_id = existing_instance.ip_id,
                                    enable_ipv6 = True,
                                    state = existing_instance.state,
                                    user_data = existing_instance.user_data,
                                    opts = ResourceOptions(import_ = existing_instance.id))
            pulumi.export("ip_address", existing_instance.public_ip)
            pulumi.export("type", existing_instance.type)
        scw_access_key = os.getenv('SCW_ACCESS_KEY')
        scw_secret_key = os.getenv('SCW_SECRET_KEY')
        scw_project_id = os.getenv('SCW_PROJECT_ID')

        stack = auto.create_or_select_stack(stack_name = hashed_instance_name,
                                            project_name = sanitize_project_name(environment['path']),
                                            program = create_pulumi_program)

        stack.set_config("scaleway:access_key", auto.ConfigValue(scw_access_key))
        stack.set_config("scaleway:secret_key", auto.ConfigValue(scw_secret_key))
        stack.set_config("scaleway:project_id", auto.ConfigValue(scw_project_id))
        log_msg("DEBUG", "[ScalewayDriver] Refreshing instance {}".format(hashed_instance_name))
        up_res = stack.up()

        return {
            "type": up_res.outputs.get("ip_address").value,
            "ip": up_res.outputs.get("type").value
        }

    def refresh_registry(self, user_email, registry_id, hashed_registry_name):
        def create_pulumi_program():
            existing_registry = scaleway.get_registry_namespace(name = hashed_registry_name, opts = None)
            pulumi.export("type", existing_registry.type)
        scw_access_key = os.getenv('SCW_ACCESS_KEY')
        scw_secret_key = os.getenv('SCW_SECRET_KEY')

        try:
            stack = auto.create_or_select_stack(stack_name = hashed_registry_name,
                                                project_name = sanitize_project_name(user_email),
                                                program = create_pulumi_program)

            stack.set_config("scaleway:access_key", auto.ConfigValue(scw_access_key))
            stack.set_config("scaleway:secret_key", auto.ConfigValue(scw_secret_key))
            log_msg("DEBUG", "[ScalewayDriver] Refreshing registry {}".format(hashed_registry_name))
            up_res = stack.up()
            return {
                "type": up_res.outputs.get("type").value
            }
        except Exception as e:
            log_msg("WARN", "[Scaleway][refresh_bucket] unexpected error: {}".format(e))
            return {
                "error": "{}".format(e)
            }

    def refresh_bucket(self, user_email, bucket_id, hashed_bucket_name):
        def create_pulumi_program():
            existing_bucket = scaleway.get_object_bucket(name = hashed_bucket_name)
            pulumi.export("type", existing_bucket.type)
        scw_access_key = os.getenv('SCW_ACCESS_KEY')
        scw_secret_key = os.getenv('SCW_SECRET_KEY')

        try:
            stack = auto.create_or_select_stack(stack_name = hashed_bucket_name,
                                                project_name = sanitize_project_name(user_email),
                                                program = create_pulumi_program)

            stack.set_config("scaleway:access_key", auto.ConfigValue(scw_access_key))
            stack.set_config("scaleway:secret_key", auto.ConfigValue(scw_secret_key))
            log_msg("DEBUG", "[ScalewayDriver] Refreshing bucket {}".format(hashed_bucket_name))
            up_res = stack.up()
            return {
                "type": up_res.outputs.get("type").value
            }
        except Exception as e:
            log_msg("WARN", "[Scaleway][refresh_bucket] unexpected error: {}".format(e))
            return {
                "error": "{}".format(e)
            }

    def get_server_state(self, server):
        switcher = {
          "stopped": "stopped",
          "rebooting": "rebooting",
          "starting": "starting",
          "stopping": "stopping",
          "running": "running"
        }

        return convert_instance_state(switcher, server)

    def get_virtual_machine(self, region, zone, instance_name):
        region_zone = "{}-{}".format(region, zone)
        sw_api_key = os.getenv('SCW_SECRET_KEY')
        res = requests.get(f'{SCW_API_URL}/instance/v1/zones/{region_zone}/servers?name={instance_name}',
                                headers = {"X-Auth-Token": sw_api_key})
        servers = res.json()['servers']
        if len(servers)>0:
            return servers[0]
        return None

    def update_virtual_machine_status(self, region, zone, server_id, action):
        regionZone = "{}-{}".format(region, zone)
        sw_api_key = os.getenv('SCW_SECRET_KEY')
        actionData = {'action':action}
        res = requests.post(f'{SCW_API_URL}/instance/v1/zones/{regionZone}/servers/{server_id}/action',
                                headers = {"X-Auth-Token": sw_api_key},
                                json = actionData)
        if res.status_code == 404:
            message = f"resource {server_id} not found."
            raise HTTPError("104", res.status_code, message, hdrs = {"i18n_code": "104"}, fp = None)

    def create_bucket(self, user_email, bucket_id, hashed_bucket_name, region, bucket_type):
        def create_pulumi_program():
            object_storage = scaleway.ObjectBucket(resource_name = hashed_bucket_name,
                                                acl = bucket_type,
                                                name = hashed_bucket_name,
                                                region = region)
            pulumi.export("endpoint", object_storage.endpoint)
        scw_access_key = os.getenv('SCW_ACCESS_KEY')
        scw_secret_key = os.getenv('SCW_SECRET_KEY')
        scw_project_id = os.getenv('SCW_PROJECT_ID')
        stack = auto.create_or_select_stack(stack_name = hashed_bucket_name,
                                            project_name = sanitize_project_name(user_email),
                                            program = create_pulumi_program)
        stack.set_config("scaleway:access_key", auto.ConfigValue(scw_access_key))
        stack.set_config("scaleway:secret_key", auto.ConfigValue(scw_secret_key))
        stack.set_config("scaleway:project_id", auto.ConfigValue(scw_project_id))
        up_res = stack.up()

        return {
            "endpoint": up_res.outputs.get("endpoint").value,
            "access_key": None,
            "secret_key": None,
            "status": "active"
        }

    def update_bucket_credentials(self, bucket):
        return {
            "access_key": None,
            "secret_key": None
        }

    def delete_bucket(self, bucket, user_email):
        hashed_bucket_name = f'{bucket.name}-{bucket.hash}'
        stack = auto.select_stack(hashed_bucket_name, sanitize_project_name(user_email), program = self.delete_bucket)
        stack.destroy()

    def create_registry(self, user_email, registry_id, hashed_name, region, type):
        def create_pulumi_program():
            isPublic = True
            if type == 'private':
                isPublic = False
            registry = scaleway.RegistryNamespace(hashed_name, name = hashed_name, region = region, is_public = isPublic)
            pulumi.export("endpoint", registry.endpoint)
        scw_access_key = os.getenv('SCW_ACCESS_KEY')
        scw_secret_key = os.getenv('SCW_SECRET_KEY')
        scw_project_id = os.getenv('SCW_PROJECT_ID')
        stack = auto.create_or_select_stack(stack_name = hashed_name,
                                            project_name = sanitize_project_name(user_email),
                                            program = create_pulumi_program)
        stack.set_config("scaleway:access_key", auto.ConfigValue(scw_access_key))
        stack.set_config("scaleway:secret_key", auto.ConfigValue(scw_secret_key))
        stack.set_config("scaleway:project_id", auto.ConfigValue(scw_project_id))
        up_res = stack.up()

        return {
            "endpoint": up_res.outputs.get("endpoint").value,
            "access_key": None,
            "secret_key": None,
            "status": "active"
        }

    def update_registry_credentials(self, registry):
        return {
            "access_key": None,
            "secret_key": None
        }

    def delete_registry(self, registry, user_email):
        hashed_name = f'{registry.name}-{registry.hash}'
        stack = auto.select_stack(hashed_name, sanitize_project_name(user_email), program = self.delete_bucket)
        stack.destroy()

    def cloud_init_script(self):
        return "cloud-init.yml"
