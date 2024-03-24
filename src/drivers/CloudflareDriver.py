from drivers.ProviderDriver import ProviderDriver

from utils.dns_zones import register_cloudflare_domain
from utils.list import unmarshall_list_array

class CloudflareDriver(ProviderDriver):
    def create_dns_records(self, record_name, environment, ip_address, root_dns_zone):
        register_cloudflare_domain(record_name, environment['path'], ip_address, root_dns_zone)
        for subdomain in unmarshall_list_array(environment['subdomains']):
            dns_record_name = "{}.{}".format(subdomain, record_name)
            register_cloudflare_domain(dns_record_name, environment['path'], ip_address, root_dns_zone)

    def cloud_init_script(self):
        return "cloud-init.yml"

    def create_instance(self, instance_id, ami_image, hashed_instance_name, environment, instance_region, instance_zone, instance_type, generate_dns, root_dns_zone):
        return {}

    def refresh_instance(self, instance_id, hashed_instance_name, environment, instance_region, instance_zone):
        return {}

    def get_server_state(self, server):
        return "starting"

    def get_virtual_machine(self, region, zone, instance_name):
        return

    def update_virtual_machine_status(self, region, zone, server_id, action):
        return

    def create_bucket(self, user_email, bucket_id, hashed_bucket_name, region, bucket_type):
        return {
            "endpoint": "https://unkown.bucket.comwork.io",
            "access_key": None,
            "secret_key": None,
            "status": "active"
        }

    def refresh_bucket(self, user_email, bucket_id, hashed_bucket_name):
        return {}

    def update_bucket_credentials(self, bucket):
        return {
            "access_key": None,
            "secret_key": None
        }

    def delete_bucket(self, bucket, user_email):
        return

    def create_registry(self, user_email, registry_id, hashed_name, region, type):
        return {
            "endpoint": "https://unkown.registry.comwork.io",
            "access_key": None,
            "secret_key": None,
            "status": "active"
        }

    def refresh_registry(self, user_email, registry_id, hashed_name, region, type):
        return

    def update_registry_credentials(self, registry):
        return {
            "access_key": None,
            "secret_key": None
        }

    def delete_registry(self, registry, user_email):
        return
