from abc import ABC, abstractmethod

class ProviderDriver(ABC):
    @abstractmethod
    def create_dns_records(self, record_name, environment, ip_address, root_dns_zone):
        pass

    @abstractmethod
    def list_dns_records(self):
        pass

    @abstractmethod
    def create_custom_dns_record(self, record_name, dns_zone, record_type, ttl, data):
        pass

    @abstractmethod
    def delete_dns_records(self, id, record_name, root_dns_zone):
        pass

    @abstractmethod
    def create_instance(self, hashed_instance_name, environment, instance_region, instance_zone, instance_type, ami_image, generate_dns, root_dns_zone):
        pass

    @abstractmethod
    def refresh_instance(self, hashed_instance_name, environment, instance_region, instance_zone):
        pass

    @abstractmethod
    def get_server_state(self, server):
        pass

    @abstractmethod
    def get_virtual_machine(self, region, zone, instance_name):
        pass

    @abstractmethod
    def update_virtual_machine_status(self, region, zone, server_id, action):
        pass

    @abstractmethod
    def create_bucket(self, user_email, hashed_bucket_name, region, bucket_type):
        pass

    @abstractmethod
    def refresh_bucket(self, user_email, hashed_bucket_name):
        pass

    @abstractmethod
    def update_bucket_credentials(self, bucket):
        pass

    @abstractmethod
    def delete_bucket(self, bucket, user_email):
        pass

    @abstractmethod
    def create_registry(self, user_email, hashed_name, region, type):
        pass

    @abstractmethod
    def refresh_registry(self, user_email, hashed_registry_name):
        pass

    @abstractmethod
    def update_registry_credentials(self, registry):
        pass

    @abstractmethod
    def delete_registry(self, registry, user_email):
        pass

    @abstractmethod
    def cloud_init_script(self):
        pass
