from drivers.ProviderDriver import ProviderDriver
from utils.logger import log_msg

class VoidDriver(ProviderDriver):
    def create_dns_records(self, record_name, environment, ip_address, root_dns_zone):
        log_msg("INFO", "[VoidDriver][create_dns_records] record_name = {}, environment = {}, ip_address = {}, root_dns_zone = {}".format(record_name, environment, ip_address, root_dns_zone))
        return

    def create_instance(self, hashed_instance_name, environment, instance_region, instance_zone, instance_type, generate_dns, ami_image, root_dns_zone):
        log_msg("INFO", "[VoidDriver][create_instance] hashed_instance_name = {}, environment = {}, instance_region = {}, instance_type = {}, ami_image = {}, generate_dns = {}, root_dns_zone = {}".format(hashed_instance_name, environment, instance_region, instance_zone, instance_type, ami_image, generate_dns, root_dns_zone))
        return {}
    
    def create_custom_dns_record(self, record_name, dns_zone, record_type, ttl, data):
        log_msg("INFO", "[VoidDriver][create_custom_dns_record] record_name = {}, dns_zone = {}, record_type = {}, ttl = {}, data = {}".format(record_name, dns_zone, record_type, ttl, data))
        return {}
    
    def delete_dns_records(self, record_id, record_name, dns_zone):
        log_msg("INFO", "[VoidDriver][delete_dns_records] record_id = {}, record_name = {}, dns_zone = {}".format(record_id, record_name, dns_zone))
        return {}
    
    def list_dns_records(self):
        log_msg("INFO", "[VoidDriver][list_dns_records]")
        return []    

    def refresh_instance(self, instance_id, hashed_instance_name, environment, instance_region, instance_zone):
        log_msg("INFO", "[VoidDriver][refresh_instance] instance_id = {}, hashed_instance_name = {}, environment = {}, instance_region = {}, instance_zone = {}".format(instance_id, hashed_instance_name, environment, instance_region, instance_zone))
        return {}

    def get_server_state(self, server):
        log_msg("INFO", "[VoidDriver][get_server_state] server = {}".format(server))
        return "starting"

    def get_virtual_machine(self, region, zone, instance_name):
        log_msg("INFO", "[VoidDriver][get_virtual_machine] region = {}, zone = {}, instance_name = {}".format(region, zone, instance_name))
        return

    def update_virtual_machine_status(self, region, zone, server_id, action):
        log_msg("INFO", "[VoidDriver][update_virtual_machine_status] region = {}, zone = {}, server_id = {}, action = {}".format(region, zone, server_id, action))
        return

    def create_bucket(self, user_email, hashed_bucket_name, region, bucket_type):
        log_msg("INFO", "[VoidDriver][create_bucket] user_email = {}, hashed_bucket_name = {}, region = {}, bucket_type = {}".format(user_email, hashed_bucket_name, region, bucket_type))
        return {
            "endpoint": "https://unkown.bucket.comwork.io",
            "access_key": None,
            "secret_key": None,
            "status": "active"
        }

    def update_bucket_credentials(self, bucket):
        log_msg("INFO", "[VoidDriver][update_bucket_credentials] bucket = {}".format(bucket))
        return {
            "access_key": None,
            "secret_key": None
        }

    def delete_bucket(self, bucket, user_email):
        log_msg("INFO", "[VoidDriver][delete_bucket] bucket = {}, user_email = {}".format(bucket, user_email))
        return

    def create_registry(self, user_email, hashed_name, region, type):
        log_msg("INFO", "[VoidDriver][create_registry] user_email = {}, hashed_name = {}, region = {}, type = {}".format(user_email, hashed_name, region, type))
        return {
            "endpoint": "https://unkown.registry.comwork.io",
            "access_key": None,
            "secret_key": None,
            "status": "active"
        }

    def update_registry_credentials(self, registry):
        log_msg("INFO", "[VoidDriver][update_registry_credentials] registry = {}".format(registry))
        return {
            "access_key": None,
            "secret_key": None
        }

    def delete_registry(self, registry, user_email):
        log_msg("INFO", "[VoidDriver][delete_registry] registry = {}, user_email = {}".format(registry, user_email))
        return

    def refresh_registry(self, user_email, hashed_registry_name):
        log_msg("INFO", "[VoidDriver][refresh_registry] user_email = {}, hashed_registry_name = {}".format(user_email, hashed_registry_name))
        return {}

    def refresh_bucket(self, user_email, hashed_bucket_name):
        log_msg("INFO", "[VoidDriver][refresh_bucket] user_email = {}, hashed_bucket_name = {}".format(user_email, hashed_bucket_name))
        return {}

    def cloud_init_script(self):
        log_msg("INFO", "[VoidDriver][cloud_init_script]")
        return "cloud-init.yml"
