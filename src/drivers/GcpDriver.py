import os
import re
import importlib
import pulumi

from pulumi_gcp import compute
import pulumi_gcp as gcp

from pulumi import automation as auto
from google.cloud import compute_v1
from google.oauth2 import service_account

from drivers.ProviderDriver import ProviderDriver

from utils.common import is_not_empty, is_true
from utils.dns_zones import get_dns_zone_driver
from utils.driver import convert_instance_state, sanitize_project_name
from utils.dynamic_name import rehash_dynamic_name
from utils.firewall import get_firewall_tags
from utils.gcp_client import _gcp_project_id, _google_app_cred_str, _google_app_credentials, update_credentials_policy_registry, delete_registry_service_account, delete_bucket_service_account, get_gcp_instance_name, update_bucket_keys, update_policy_and_credentials_bucket, update_registry_token
from utils.logger import log_msg

class GcpDriver(ProviderDriver):
    def create_dns_records(self, record_name, environment, ip_address, root_dns_zone):
        return

    def create_instance(self, instance_id, ami_image, hashed_instance_name, environment, instance_region, instance_zone, instance_type, generate_dns, root_dns_zone):
        def create_pulumi_program():
            ip_address = gcp.compute.Address(
                "external-ip",
                address_type = "EXTERNAL",
                region = instance_region
            )

            firewall_tags = get_firewall_tags()
            gcp_network = os.getenv('GCP_NETWORK')

            compute_firewall = compute.Firewall(
                "cwc-firewall",
                project = _gcp_project_id,
                network = gcp_network,
                source_tags = firewall_tags,
                allows = [compute.FirewallAllowArgs(protocol = "tcp", ports = ["22", "80", "443"])]
            )

            if re.match("^projects\/", ami_image):
                link_ami_image = ami_image
            else:
                link_ami_image = f'projects/{_gcp_project_id}/global/images/{ami_image}'

            log_msg("DEBUG", "[GcpDriver][create_instance] hashed_instance_name = {}, link_ami_image = {}".format(hashed_instance_name, link_ami_image))
            compute_instance = compute.Instance(
                resource_name = hashed_instance_name,
                name = hashed_instance_name,
                tags = firewall_tags,
                project = _gcp_project_id,
                machine_type = instance_type,
                zone = f'{instance_region}-{instance_zone}',
                boot_disk = compute.InstanceBootDiskArgs(
                    initialize_params = compute.InstanceBootDiskInitializeParamsArgs(
                        type = 'pd-standard',
                        size = 50,
                        image = link_ami_image,
                    ),
                ),
                network_interfaces = [{
                    "network": compute_firewall.network,
                    "accessConfigs": [{
                        "nat_ip": ip_address.address,
                    }],
                }],
                service_account = compute.InstanceServiceAccountArgs(
                    scopes = ["https://www.googleapis.com/auth/cloud-platform"],
                ),
                metadata_startup_script = (lambda path: open(path).read())(self.cloud_init_script()))

            pulumi.export("public_ip", compute_instance.network_interfaces[0].access_configs[0].nat_ip)
            if is_true(generate_dns):
                dns_driver = get_dns_zone_driver(root_dns_zone)
                ProviderDriverModule = importlib.import_module('drivers.{}'.format(dns_driver))
                ProviderDriver = getattr(ProviderDriverModule, dns_driver)
                ProviderDriver().create_dns_records(hashed_instance_name, environment, compute_instance.network_interfaces[0].access_configs[0].nat_ip, root_dns_zone)

        cloudflare_api_token = os.getenv('CLOUDFLARE_API_TOKEN')
        stack = auto.create_or_select_stack(stack_name = hashed_instance_name,
                                            project_name = sanitize_project_name(environment['path']),
                                            program = create_pulumi_program)

        stack.set_config("gcp:project", auto.ConfigValue(_gcp_project_id))
        stack.set_config("gcp:credentials", auto.ConfigValue(_google_app_cred_str))
        stack.set_config("gcp:region", auto.ConfigValue(instance_region))

        if is_not_empty(cloudflare_api_token):
            stack.set_config("cloudflare:api_token", auto.ConfigValue(cloudflare_api_token))
        up_res = stack.up()

        return {
            "ip": up_res.outputs.get("public_ip").value
        }

    def cloud_init_script(self):
        return "cloud-init.sh"

    def refresh_instance(self, instance_id, hashed_instance_name, environment, instance_region, instance_zone):
        return {}

    def create_bucket(self, user_email, bucket_id, hashed_bucket_name, region, bucket_type):
        def create_pulumi_program():
            bucket = gcp.storage.Bucket(hashed_bucket_name, location = region)
            pulumi.export("endpoint", bucket.self_link)

        stack = auto.create_or_select_stack(stack_name = hashed_bucket_name,
                                            project_name = sanitize_project_name(user_email),
                                            program = create_pulumi_program)

        stack.set_config("gcp:project", auto.ConfigValue(_gcp_project_id))
        stack.set_config("gcp:credentials", auto.ConfigValue(_google_app_cred_str))
        stack.set_config("gcp:zone", auto.ConfigValue(region))
        try:
            up_res = stack.up()
        except Exception as e:
            log_msg("ERROR", "[GcpDriver][create_bucket] unexpected exception : e = {}".format(e))

        (access_id, secret_id, service_account_id) = update_policy_and_credentials_bucket(hashed_bucket_name, bucket_type)

        return {
            "endpoint": up_res.outputs.get("endpoint").value,
            "user_id": service_account_id,
            "access_key": access_id,
            "secret_key": secret_id,
            "status": "active"
        }

    def create_registry(self, user_email, registry_id, hashed_name, region, type):
        def create_pulumi_program():
            gcp.artifactregistry.Repository(hashed_name,
                 description = "Docker repository",
                 format = "DOCKER",
                 location = region,
                 repository_id = hashed_name)

            pulumi.export("endpoint", f"{region}-docker.pkg.dev/{_gcp_project_id}/{hashed_name}")

        stack = auto.create_or_select_stack(stack_name = hashed_name,
                                            project_name = sanitize_project_name(user_email),
                                            program = create_pulumi_program)

        stack.set_config("gcp:project", auto.ConfigValue(_gcp_project_id))
        stack.set_config("gcp:credentials", auto.ConfigValue(_google_app_cred_str))
        stack.set_config("gcp:zone", auto.ConfigValue(region))

        up_res = stack.up()

        service_account_acess_key = update_credentials_policy_registry(hashed_name, region, type)

        return {
            "endpoint": up_res.outputs.get("endpoint").value,
            "access_key": service_account_acess_key,
            "status": "active"
        }

    def get_server_state(self, server):
        switcher = {
            "running": "running",
            "stopping": "stopped",
            "stopped": "stopped",
            "terminated": "deleted",
            "provisioning": "starting",
            "staging": "starting",
            "repairing": "running",
            "suspending": "stopped",
            "suspended": "stopped"
        }

        return convert_instance_state(switcher, server)

    def get_virtual_machine(self, region, zone, instance_name):
        availibility_zone = f'{region}-{zone}'

        name = get_gcp_instance_name(zone = availibility_zone, name_instance = instance_name)
        credentials = service_account.Credentials.from_service_account_info(
            _google_app_credentials,
            scopes = ['https://www.googleapis.com/auth/cloud-platform'])

        client = compute_v1.InstancesClient(credentials = credentials)
        instance_info = client.get(project = _gcp_project_id, zone = availibility_zone, instance = name)
        gcp_server = {
            "id": instance_info.id,
            "state": instance_info.status
        }
        if instance_info.name != "":
            return gcp_server
        else:
            return None

    def update_virtual_machine_status(self, region, zone, server_id, action):
        availibility_zone = f'{region}-{zone}'

        credentials = service_account.Credentials.from_service_account_info(
            _google_app_credentials,
            scopes = ['https://www.googleapis.com/auth/cloud-platform'])
        client = compute_v1.InstancesClient(credentials = credentials)

        i_name = client.get(project = _gcp_project_id, zone = availibility_zone, instance = str(server_id)).name
        if action == "poweroff":
            client.stop(project = _gcp_project_id, zone = availibility_zone, instance = i_name)
        elif action == "reboot":
            client.reset(project = _gcp_project_id, zone = availibility_zone, instance = i_name)
        elif action == "poweron":
            client.start(project = _gcp_project_id, zone = availibility_zone, instance = i_name)

    def refresh_bucket(self, user_email, bucket_id, hashed_bucket_name):
        log_msg("INFO", "[gcpDriver][refresh_bucket] bucket_id = {}, user_email = {}, hashed_bucket_name = {}".format(bucket_id, user_email, hashed_bucket_name))
        return {}

    def update_bucket_credentials(self, bucket):
        hashed_bucket_name = rehash_dynamic_name(bucket.name, bucket.hash)
        (access_id, secret_id) = update_bucket_keys(hashed_bucket_name)
        return {
            "access_key": access_id,
            "secret_key": secret_id
        }

    def delete_bucket(self, bucket, user_email):
        hashed_bucket_name = rehash_dynamic_name(bucket.name, bucket.hash)
        bucket.force_delete_objects = True
        service_account_email = f"{hashed_bucket_name}-sa@{_gcp_project_id}.iam.gserviceaccount.com"
        stack = auto.select_stack(hashed_bucket_name, user_email, program = self.delete_bucket)
        stack.destroy()
        delete_bucket_service_account(service_account_email)

    def refresh_registry(self, user_email, registry_id, hashed_registry_name):
        log_msg("INFO", "[gcpDriver][refresh_registry] registry_id = {}, user_email = {}, hashed_registry_name = {}".format(registry_id, user_email, hashed_registry_name))
        return {}

    def update_registry_credentials(self, registry):
        hashed_name = rehash_dynamic_name(registry.name, registry.hash)
        access_key = update_registry_token(hashed_name)
        return {
            'access_key': access_key
        }

    def delete_registry(self, registry, user_email):
        hashed_name = rehash_dynamic_name(registry.name, registry.hash)
        service_account_email = f"{hashed_name}-sa@{_gcp_project_id}.iam.gserviceaccount.com"
        stack = auto.select_stack(hashed_name, user_email, program = self.delete_registry)
        stack.destroy()
        delete_registry_service_account(service_account_email)
