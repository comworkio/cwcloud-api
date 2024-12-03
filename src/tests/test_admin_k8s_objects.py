from unittest import TestCase
from unittest.mock import Mock, patch, MagicMock
from fastapi.responses import JSONResponse, PlainTextResponse
import json
import yaml

test_current_user = Mock()
mock_db = Mock()
mock_bt = Mock()
sample_object_representation = {"apiVersion": "v1","kind": "Pod","metadata": {"name": "test-pod"},}  
sample_object_yaml = yaml.dump(sample_object_representation)

class TestAdminK8sObjects(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestAdminK8sObjects, self).__init__(*args, **kwargs)
       
    @patch('controllers.admin.admin_k8s_objects.get_cluster_services', side_effect=lambda current_user, cluster_id, db: {'id': '11', 'content': "test", 'created_at': '111', 'owner_id': '111'}) 
    def test_get_cluster_services(self, get_cluster_services):
        # Given
        from controllers.admin.admin_k8s_objects import get_cluster_services
        
        # When
        result = get_cluster_services(test_current_user, '1', mock_db)

        # Then
        self.assertEqual(result, {'id': '11', 'content': "test", 'created_at': '111', 'owner_id': '111'})
        
    @patch('controllers.admin.admin_k8s_objects.get_cluster_general_services', side_effect=lambda current_user, cluster_id, db: JSONResponse(content=[{'name': 'test-service', 'namespace': 'test-namespace'}], status_code=200))
    def test_get_cluster_general_services(self, get_cluster_general_services):
        # Given
        from controllers.admin.admin_k8s_objects import get_cluster_general_services

        # When
        result = get_cluster_general_services(test_current_user, '1', mock_db)

        # Then
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(json.loads(result.body), [{'name': 'test-service', 'namespace': 'test-namespace'}])
            
    @patch('controllers.admin.admin_k8s_objects.get_cluster_general_namespaces', side_effect=lambda current_user, cluster_id, db: JSONResponse(content=['namespace1', 'namespace2'], status_code=200))
    def test_get_cluster_general_namespaces(self, get_cluster_general_namespaces):
        # Given
        from controllers.admin.admin_k8s_objects import get_cluster_general_namespaces
        
        # When
        result = get_cluster_general_namespaces(test_current_user, '1', mock_db)

        # Then
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(json.loads(result.body), ['namespace1', 'namespace2'])        
        
    @patch('controllers.admin.admin_k8s_objects.get_cluster_config_maps', side_effect=lambda current_user, cluster_id, db: JSONResponse(content=[{'name': 'configmap1', 'namespace': 'namespace1', 'data_type': ['key1'], 'creation_date': '2023-04-01T12:00:00.000000'}, {'name': 'configmap2', 'namespace': 'namespace2', 'data_type': ['key2'], 'creation_date': '2023-04-01T12:00:00.000000'}], status_code=200))
    def test_get_cluster_config_maps(self, get_cluster_config_maps):
        # Given
        from controllers.admin.admin_k8s_objects import get_cluster_config_maps
        
        # When
        result = get_cluster_config_maps(test_current_user, '1', mock_db)

        # Then
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(json.loads(result.body), [{'name': 'configmap1', 'namespace': 'namespace1', 'data_type': ['key1'], 'creation_date': '2023-04-01T12:00:00.000000'}, {'name': 'configmap2', 'namespace': 'namespace2', 'data_type': ['key2'], 'creation_date': '2023-04-01T12:00:00.000000'}])

    @patch('controllers.admin.admin_k8s_objects.get_cluster_ingresses', side_effect=lambda current_user, cluster_id, db: JSONResponse(content=[{
        "name": "ingress1",
        "namespace": "namespace1",
        "creation_date": "2023-04-01T12:00:00.000000",
        "ingressClassName": "nginx",
        "targets": [{
            "host": "example.com",
            "target_service": "service1",
            "target_service_port": 80,
            "path": "/",
            "path_type": "Prefix"
        }]
    }], status_code=200))
    def test_get_cluster_ingresses(self, get_cluster_ingresses):
        # Given
        from controllers.admin.admin_k8s_objects import get_cluster_ingresses
        
        # When
        result = get_cluster_ingresses(test_current_user, '1', mock_db)

        # Then
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(json.loads(result.body), [{
            "name": "ingress1",
            "namespace": "namespace1",
            "creation_date": "2023-04-01T12:00:00.000000",
            "ingressClassName": "nginx",
            "targets": [{
                "host": "example.com",
                "target_service": "service1",
                "target_service_port": 80,
                "path": "/",
                "path_type": "Prefix"
            }]
        }])
            
    @patch('controllers.admin.admin_k8s_objects.get_cluster_secrets', side_effect=lambda current_user, cluster_id, db: JSONResponse(content=[{
        "name": "secret1",
        "namespace": "namespace1",
        "creation_date": "2023-04-01T12:00:00.000000",
        "type": "Opaque"
    }], status_code=200))
    def test_get_cluster_secrets(self, get_cluster_secrets):
        # Given
        from controllers.admin.admin_k8s_objects import get_cluster_secrets

        # When
        result = get_cluster_secrets(test_current_user, '1', mock_db)

        # Then
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(json.loads(result.body), [{
            "name": "secret1",
            "namespace": "namespace1",
            "creation_date": "2023-04-01T12:00:00.000000",
            "type": "Opaque"
        }])
            
    @patch('controllers.admin.admin_k8s_objects.get_cluster_ingress_classes', side_effect=lambda current_user, cluster_id, db: JSONResponse(content=[{
        "name": "ingress1",
        "namespace": "namespace1",
        "creation_date": "2023-04-01T12:00:00.000000",
        "ingressClassName": "nginx",
        "targets": [{
            "host": "example.com",
            "target_service": "service1",
            "target_service_port": 80,
            "path": "/",
            "path_type": "Prefix"
        }]
    }], status_code=200))
    def test_get_cluster_ingress_classes(self, get_cluster_ingress_classes):
        # Given
        from controllers.admin.admin_k8s_objects import get_cluster_ingress_classes
        
        # When
        result = get_cluster_ingress_classes(test_current_user, '1', mock_db)

        # Then
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(json.loads(result.body), [{
            "name": "ingress1",
            "namespace": "namespace1",
            "creation_date": "2023-04-01T12:00:00.000000",
            "ingressClassName": "nginx",
            "targets": [{
                "host": "example.com",
                "target_service": "service1",
                "target_service_port": 80,
                "path": "/",
                "path_type": "Prefix"
            }]
        }])
        
    @patch('entities.kubernetes.Cluster.Cluster.getById', side_effect = lambda id, db:{'id' : '1'})
    @patch('entities.kubernetes.KubeconfigFile.KubeConfigFile')
    @patch('utils.yaml.read_uploaded_yaml_file')
    @patch('constants.k8s_constants.K8S_RESOURCES')
    @patch('controllers.admin.admin_k8s_objects.update_object', side_effect=lambda current_user, object, yaml_file, db: {
        'status': 'ok',
        'message': 'Successfully updated object',
    })    
    def test_update_object(self, update_object, mock_upload_file, mock_read_uploaded_yaml_file, mock_delete_resource, findOne):
        # Given
        from controllers.admin.admin_k8s_objects import update_object
        from entities.kubernetes.Cluster import Cluster
        from entities.kubernetes.KubeconfigFile import KubeConfigFile
        from schemas.Kubernetes import ObjectSchema

        kubeconfigfile = KubeConfigFile()
        kubeconfigfile.id = 1
        kubeconfigfile.content = b'my_binary_content'
        kubeconfigfile.created_at = 'test'
        kubeconfigfile.owner_id = 1
        KubeConfigFile.findOne.return_value = kubeconfigfile
        
        cluster = Cluster()
        cluster.id = 1
        cluster.name = "cluster1"
        cluster.kubeconfig_file_id = "1111111"
        cluster.version = "test"
        cluster.platform = "cluster1 platform"
        cluster.created_at = "cluster1 created at"
        Cluster.getById.return_value = cluster
        
        mock_yaml_content = MagicMock()
        mock_read_uploaded_yaml_file.return_value = mock_yaml_content
        
        mock_delete_resource.return_value = None
        mock_upload_file.return_value = None

        object_schema = ObjectSchema(
            kind='Pod',
            cluster_id='1',
            name='test-pod',
            namespace='default'
        )
        
        # When
        result = update_object(test_current_user, object_schema, mock_upload_file, mock_db)
        
        # Then
        self.assertEqual(result, {
            'status': 'ok',
            'message': 'Successfully updated object'
        })
 
    @patch('entities.kubernetes.Cluster.Cluster.getById', side_effect = lambda id, db:{'id' : '1'})
    @patch('entities.kubernetes.KubeconfigFile.KubeConfigFile')
    @patch('utils.yaml.read_uploaded_yaml_file')
    @patch('controllers.admin.admin_k8s_objects.get_object', return_value=PlainTextResponse(content=sample_object_yaml, status_code=200))
    def test_get_object(self, read_uploaded_yaml_file, get_object, findOne, getById):
        # Given
        from controllers.admin.admin_k8s_objects import get_object
        from schemas.Kubernetes import ObjectSchema
        from entities.kubernetes.Cluster import Cluster
        from entities.kubernetes.KubeconfigFile import KubeConfigFile
        
        kubeconfigfile = KubeConfigFile()
        kubeconfigfile.id = 1
        kubeconfigfile.content = b'my_binary_content'
        kubeconfigfile.created_at = 'test'
        kubeconfigfile.owner_id = 1
        KubeConfigFile.findOne.return_value = kubeconfigfile
        
        cluster = Cluster()
        cluster.id = 1
        cluster.name = "cluster1"
        cluster.kubeconfig_file_id = "1111111"
        cluster.version = "test"
        cluster.platform = "cluster1 platform"
        cluster.created_at = "cluster1 created at"
        Cluster.getById.return_value = cluster
        
        object_schema = ObjectSchema(
                    kind='Pod',
                    cluster_id='1',
                    name='test-pod',
                    namespace='default'
                )
        
        # When
        result = get_object(test_current_user, object_schema, mock_db)

        # Then
        self.assertEqual(result.status_code, 200)
