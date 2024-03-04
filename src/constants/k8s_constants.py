K8S_OBJECTS = {
    'service': 'Service',
    'ingress': 'Ingress',
    'configmap': 'ConfigMap',
    'secret': 'Secret',
}

K8S_RESOURCES = {
    'service': {
        'api_version': 'v1',
        'api_group': '',
        'plural': 'services',
    },
    'deployment': {
        'api_version': 'apps/v1',
        'api_group': 'apps',
        'plural': 'deployments',
    },
    'service-account': {
        'api_version': 'v1',
        'api_group': '',
        'plural': 'serviceaccounts',
    },
    'hpod-autoscaler': {
        'api_version': 'autoscaling/v1',
        'api_group': 'autoscaling',
        'plural': 'horizontalpodautoscalers',
    },
    'ingress': {
        'api_version': 'networking.k8s.io/v1',
        'api_group': 'networking.k8s.io',
        'plural': 'ingresses',
    },
    'configmap': {
        'api_version': 'v1',
        'api_group': '',
        'plural': 'configmaps',
    },
    'persistent-volume': {
        'api_version': 'v1',
        'api_group': '',
        'plural': 'persistentvolumes',
    },
    'secret': {
        'api_version': 'v1',
        'api_group': '',
        'plural': 'secrets',
    },
}

FLUX_FILE_URL = 'https://github.com/fluxcd/flux2/releases/latest/download/install.yaml'
