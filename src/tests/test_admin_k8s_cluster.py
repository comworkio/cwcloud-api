from unittest import TestCase
from unittest.mock import Mock, patch, MagicMock

test_current_user = Mock()
mock_db = Mock()
mock_bt = Mock()

class TestAdminK8sCluster(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestAdminK8sCluster, self).__init__(*args, **kwargs)
    
    @patch('controllers.admin.admin_k8s_cluster.get_all_clusters', side_effect=lambda db: {'status_code': 200, 'json': {'status': 'ok', 'message': 'kubeconfig successfully uploaded', 'file_id': 1}})
    @patch('entities.kubernetes.Cluster.Cluster')   
    def test_get_all_clusters(self, getAll, get_all_clusters):
        # Given
        from controllers.admin.admin_k8s_cluster import get_all_clusters
        from entities.kubernetes.Cluster import Cluster
        
        cluster = Cluster()
        cluster.id = 1
        cluster.name = "cluster1"
        cluster.kubeconfig_file_id = "1111111"
        cluster.version = "test"
        cluster.platform = "cluster1 platform"
        cluster.created_at = "cluster1 created at"
        
        getAll.return_value = [cluster]
        
        # When
        result = get_all_clusters(mock_db)

        # Then
        self.assertEqual(result['status_code'], 200)
        self.assertEqual(result['json'], {
            'status': 'ok',
            'message': 'kubeconfig successfully uploaded',
            'file_id': cluster.id
        })
      
    @patch('controllers.admin.admin_k8s_cluster.get_cluster', side_effect=lambda cluster_id, db: {'id': '1', 'user_id': "testuser@example.com"})
    @patch('entities.kubernetes.Cluster.Cluster')   
    def test_get_cluster(self, getById, get_cluster):
        # Given
        from controllers.admin.admin_k8s_cluster import get_cluster
        from entities.kubernetes.Cluster import Cluster
        
        cluster = Cluster()
        cluster.id = 1
        cluster.name = "cluster1"
        cluster.kubeconfig_file_id = "1111111"
        cluster.version = "test"
        cluster.platform = "cluster1 platform"
        cluster.created_at = "cluster1 created at"
        
        getById.return_value = cluster
        
        # When
        result = get_cluster('1', mock_db)

        # Then
        self.assertEqual(result, {'id': '1', 'user_id': "testuser@example.com"})
      
    @patch('controllers.admin.admin_k8s_cluster.get_clusters_byKubeconfigFile', side_effect=lambda current_user, kubeconfig_file_id, db: {'status': 'ok', 'message': 'kubeconfig successfully uploaded', 'file_id': 'kubeconfig_file_id'})
    @patch('entities.kubernetes.Cluster.Cluster')   
    def test_get_clusters_byKubeconfigFile(self, findByKubeConfigFile, get_clusters_byKubeconfigFile):
        # Given
        from controllers.admin.admin_k8s_cluster import get_clusters_byKubeconfigFile
        from entities.kubernetes.Cluster import Cluster
        
        cluster = Cluster()
        cluster.id = 1
        cluster.name = "cluster1"
        cluster.kubeconfig_file_id = "1111111"
        cluster.version = "test"
        cluster.platform = "cluster1 platform"
        cluster.created_at = "cluster1 created at"
        
        Cluster.findByKubeConfigFile.return_value = cluster
        
        # When
        result = get_clusters_byKubeconfigFile(test_current_user, '1', mock_db)

        # Then
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['message'], 'kubeconfig successfully uploaded')
        self.assertEqual(result['file_id'], 'kubeconfig_file_id')
        
    @patch('controllers.admin.admin_k8s_cluster.delete_cluster_by_id', return_value={'status': 'ok', 'message': 'Cluster successfully deleted'})
    @patch('entities.kubernetes.Cluster.Cluster.deleteOne')
    @patch('controllers.admin.admin_k8s_cluster.get_cluster')
    def test_delete_cluster_by_id(self, get_cluster, deleteOne, delete_cluster_by_id):
        # Given
        from controllers.admin.admin_k8s_cluster import delete_cluster_by_id, get_cluster
        from entities.kubernetes.Cluster import Cluster
        
        cluster = Cluster()
        cluster.id = 1
        cluster.name = "cluster1"
        cluster.kubeconfig_file_id = "1111111"
        cluster.version = "test"
        cluster.platform = "cluster1 platform"
        cluster.created_at = "cluster1 created at"
        
        get_cluster.return_value = cluster
        deleteOne.return_value = None

        # When
        result = delete_cluster_by_id(test_current_user, '1', mock_db)

        # Then
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['message'], 'Cluster successfully deleted')

    @patch('controllers.admin.admin_k8s_cluster.get_cluster_infos', side_effect=lambda current_user, cluster_id, db: {'status_code': 200})
    @patch('entities.kubernetes.KubeconfigFile.KubeConfigFile')
    @patch('utils.yaml.read_uploaded_yaml_file')
    def test_get_cluster_infos(self, findOne, get_cluster_infos, mock_read_uploaded_yaml_file):
        # Given
        from controllers.admin.admin_k8s_cluster import get_cluster_infos, get_cluster
        from entities.kubernetes.KubeconfigFile import KubeConfigFile

        kubeconfigfile = KubeConfigFile()
        kubeconfigfile.id = 1
        kubeconfigfile.content = b'my_binary_content'
        kubeconfigfile.created_at = 'test'
        kubeconfigfile.owner_id = 1
        KubeConfigFile.findOne.return_value = kubeconfigfile
        
        mock_yaml_content = MagicMock()
        mock_read_uploaded_yaml_file.return_value = mock_yaml_content
        
        # When
        result = get_cluster_infos(test_current_user, '1', mock_db)

        # Then
        self.assertEqual(result['status_code'], 200)
