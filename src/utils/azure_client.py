import os
import yaml
def get_azure_informations_by_region(instance_region):
	config_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..', 'cloud_environments.yml'))
	data = {}
	with open(config_path, "r") as stream:
		loaded_data = yaml.safe_load(stream)
		if "providers" not in loaded_data.keys():
			return None
		providers = loaded_data["providers"]
		for provider in providers:
			if provider['name'] == "azure":
				for region in provider['regions']:
					if region["name"] == instance_region:
						data['az_virtual_network_name']=region["az_virtual_network_name"]
						data['az_subnet_name']=region["az_subnet_name"]
						data['az_security_group_name']=region["az_security_group_name"]
						return data
		return None


