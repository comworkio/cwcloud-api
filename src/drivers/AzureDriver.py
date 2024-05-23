import pulumi
import os
import importlib
import base64
import pulumi_azure_native as azure_native
from utils.common import is_not_empty, is_true
from pulumi_azure_native import resources, network, compute
from pulumi import automation as auto
from utils.azure_client import get_azure_informations_by_region
from drivers.ProviderDriver import ProviderDriver
from utils.logger import log_msg
from utils.dns_zones import get_dns_zone_driver, register_azure_domain
from utils.list import unmarshall_list_array
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.core.exceptions import HttpResponseError
from utils.state import convert_instance_state

_azure_client_resource_group = os.getenv('AZURE_RESOURCE_GROUP_NAME')
_azure_client_id = os.getenv('AZURE_CLIENT_ID')
_azure_client_secret = os.getenv('AZURE_CLIENT_SECRET')
_azure_tenant_id = os.getenv('AZURE_TENANT_ID')
_azure_subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')

class AzureDriver(ProviderDriver):
    def create_instance(self, instance_id, ami_image, hashed_instance_name, environment, instance_region, instance_zone, instance_type, generate_dns, root_dns_zone):
        def create_pulumi_program():
            az_infos = get_azure_informations_by_region(instance_region)
            if az_infos is None:
                log_msg("INFO", "[get_azure_informations] az_virtual_network_name, az_subnet_name, az_security_group_name are missing")
                return None
            az_vnet = az_infos["az_virtual_network_name"]
            az_subnet = az_infos["az_subnet_name"]
            az_security_group = az_infos["az_security_group_name"]
            # Encode the userdata script to base64 to supply it to the Azure VM.
            encoded_user_data = base64.b64encode((lambda path: open(path).read())(self.cloud_init_script()).encode('utf-8')).decode('utf-8')
            resource_group_name = _azure_client_resource_group                            
            public_ip = network.PublicIPAddress(
                "ip_address",
                location=instance_region,
                public_ip_address_name=f"{hashed_instance_name}-public-ip",
                resource_group_name=resource_group_name,
                public_ip_allocation_method=network.IPAllocationMethod.STATIC,
                sku=network.PublicIPAddressSkuArgs(
                    name=network.PublicIPAddressSkuName.STANDARD,
                )
            )   
            # Create a network interface with the virtual network, IP address, and security group
            network_interface = network.NetworkInterface(
                "network-interface",
                resource_group_name=resource_group_name,
                network_security_group=network.NetworkSecurityGroupArgs(
                    id=f"/subscriptions/{_azure_subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/networkSecurityGroups/{az_security_group}",
                ),
                ip_configurations=[
                    network.NetworkInterfaceIPConfigurationArgs(
                        name=f"{hashed_instance_name}-ipconfiguration",
                        private_ip_allocation_method=network.IpAllocationMethod.DYNAMIC,
                        subnet=network.SubnetArgs(
                            id=f"/subscriptions/{_azure_subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/virtualNetworks/{az_vnet}/subnets/{az_subnet}",
                        ),
                        public_ip_address=network.PublicIPAddressArgs(
                            id=public_ip.id,
                        ),
                    ),
                ],
                network_interface_name=f"{hashed_instance_name}-network-interface"
            )
            # Create the virtual machine
            compute.VirtualMachine(
                resource_name = hashed_instance_name,
                vm_name = hashed_instance_name,
                resource_group_name=resource_group_name,
                network_profile=compute.NetworkProfileArgs(
                    network_interfaces=[
                        compute.NetworkInterfaceReferenceArgs(
                            id=network_interface.id,
                            primary=True,
                        )
                    ]
                ),
                hardware_profile=compute.HardwareProfileArgs(
                    vm_size="Standard_DS2_v2",
                ),
                os_profile=compute.OSProfileArgs(
                    computer_name=hashed_instance_name,
                    admin_username="devops",
                    admin_password="Cloud-456",
                    linux_configuration=compute.LinuxConfigurationArgs(
                        disable_password_authentication=False
                    )
                ),
                storage_profile=compute.StorageProfileArgs(
                    image_reference=compute.ImageReferenceArgs(
                        id=f"/subscriptions/{_azure_subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Compute/images/{ami_image}",
                    ),
                    os_disk={
                        "caching": compute.CachingTypes.READ_WRITE,
                        "createOption": "FromImage",
                        "managedDisk": compute.ManagedDiskParametersArgs(
                            storage_account_type="Standard_LRS",
                        ),
                        "name": f"{hashed_instance_name}-myVMosdisk",
                    },
                ),
                user_data=encoded_user_data,
            )
            if generate_dns == "true":
                dns_driver = get_dns_zone_driver(root_dns_zone)
                ProviderDriverModule = importlib.import_module('drivers.{}'.format(dns_driver))
                ProviderDriver = getattr(ProviderDriverModule, dns_driver)
                ProviderDriver().create_dns_records(hashed_instance_name, environment, public_ip.ip_address, root_dns_zone)
            pulumi.export("publicIpAddress", public_ip.ip_address)
        cloudflare_api_token = os.getenv('CLOUDFLARE_API_TOKEN')
        stack = auto.create_or_select_stack(stack_name = hashed_instance_name,
        project_name = environment['path'],
        program = create_pulumi_program)
        stack.set_config("azure-native:environment", auto.ConfigValue("public"))
        stack.set_config("azure-native:clientId", auto.ConfigValue(_azure_client_id))
        stack.set_config("azure-native:clientSecret", auto.ConfigValue(_azure_client_secret, secret=True))
        stack.set_config("azure-native:tenantId", auto.ConfigValue(_azure_tenant_id))
        stack.set_config("azure-native:subscriptionId", auto.ConfigValue(_azure_subscription_id))
        stack.set_config("azure-native:location", auto.ConfigValue(instance_region))
        if is_not_empty(cloudflare_api_token):
            stack.set_config("cloudflare:apiToken", auto.ConfigValue(cloudflare_api_token, secret=True))         
        up_res = stack.up()
        return {
            "ip": up_res.outputs.get("publicIpAddress").value
        }
    def cloud_init_script(self):
        return "cloud-init.yml"
    def create_dns_records(self, record_name, environment, ip_address, root_dns_zone):
        register_azure_domain(record_name, environment['path'], ip_address, root_dns_zone)
        for subdomain in unmarshall_list_array(environment['subdomains']):
            dns_record_name = "{}.{}".format(subdomain, record_name)
            register_azure_domain(dns_record_name, environment['path'], ip_address, root_dns_zone)
    def refresh_instance(self, instance_id, hashed_instance_name, environment, instance_region, instance_zone):
        return
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
        subscription_id = _azure_subscription_id
        resource_group_name = _azure_client_resource_group
        credential = DefaultAzureCredential()
        compute_client = ComputeManagementClient(credential, subscription_id)
        try:
            virtual_machine = compute_client.virtual_machines.get(resource_group_name, instance_name, expand='instanceView')
            vm_state = virtual_machine.instance_view.statuses[1].display_status  # Assuming the state is at index 1 in the statuses list
            return {
                "id": virtual_machine.id,
                "state": vm_state.split()[1]
            }
        except HttpResponseError as ex:
            log_msg("INFO", "[get_virtual_machine_azure] An error occurred while fetching VM {}: {}".format(instance_name, ex))
            return None
        except IndexError:
            log_msg("INFO", "[get_virtual_machine_azure] Unable to determine the state of VM  {}".format(instance_name))
            return None
        except Exception as ex:
            log_msg("INFO", "[get_virtual_machine_azure] An unexpected error occurred:  {}".format(ex))
            return None
    def update_virtual_machine_status(self, region, zone, server_id, action):
        subscription_id = _azure_subscription_id
        resource_group_name = _azure_client_resource_group
        instance_name = server_id.split('/')[-1]
        credential = DefaultAzureCredential()
        compute_client = ComputeManagementClient(credential, subscription_id)
        try:
            if action == "poweroff":
                compute_client.virtual_machines.begin_power_off(resource_group_name, instance_name).wait()
                log_msg("INFO", "[poweroff_machine_azure] vm {} powered off".format(instance_name))
            elif action == "reboot":
                compute_client.virtual_machines.begin_restart(resource_group_name, instance_name).wait()
                log_msg("INFO", "[reboot_machine_azure] reboot vm {}".format(instance_name))
            elif action == "poweron":
                compute_client.virtual_machines.begin_start(resource_group_name, instance_name).wait()
                log_msg("INFO", "[poweron_machine_azure] vm {} powered on".format(instance_name))
        
        except Exception as ex:
            log_msg("INFO", "[update_virtual_machine_status] An unexpected error occurred:  {}".format(ex))                    
    def create_bucket(self, user_email, bucket_id, hashed_bucket_name, region, bucket_type):
        return        
    def update_bucket_credentials(self, bucket, user_email):
        return
    def delete_bucket(self, bucket, user_email):
        return
    def create_registry(self, user_email, registry_id, hashed_name, region, type):
        return
    def update_registry_credentials(self, registry, user_email):
        return
    def delete_registry(self, registry, user_email):
        return
    def refresh_registry(self, user_email, registry_id, hashed_registry_name):
        return {}
    def refresh_bucket(self, user_email, bucket_id, hashed_bucket_name):
        return
