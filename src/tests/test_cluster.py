from unittest import TestCase
from unittest.mock import Mock, patch
from fastapi.responses import JSONResponse
import json

test_current_user = Mock()
mock_db = Mock()
mock_bt = Mock()

class TestK8sCluster(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestK8sCluster, self).__init__(*args, **kwargs)
        
    @patch('controllers.kubernetes.cluster.get_clusters_limited', side_effect=lambda current_user, db: JSONResponse(content=[{
            'id': '1',
           'name': 'cluster1',
           'kubeconfig_file_id': '1111111',
           'version': 'test',
           'platform': 'cluster1 platform',
           'created_at': 'cluster1 created at'
    }], status_code=200))
    @patch('entities.kubernetes.Cluster.Cluster.getAllForUser')   
    @patch('utils.kubernetes.k8s_management.get_dumped_json')
    def test_get_clusters_limited(self, getAllForUser, get_dumped_json, get_clusters_limited):
        # Given
        from controllers.kubernetes.cluster import get_clusters_limited
        from entities.kubernetes.Cluster import Cluster
        
        cluster = Cluster()
        cluster.id = 1
        cluster.name = "cluster1"
        cluster.kubeconfig_file_id = "1111111"
        cluster.version = "test"
        cluster.platform = "cluster1 platform"
        cluster.created_at = "cluster1 created at"
        
        Cluster.getAllForUser.return_value = cluster
        
        # When
        result = get_clusters_limited(test_current_user, mock_db)

        # Then
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(json.loads(result.body), [{
           'id': '1',
           'name': 'cluster1',
           'kubeconfig_file_id': '1111111',
           'version': 'test',
           'platform': 'cluster1 platform',
           'created_at': 'cluster1 created at'
        }])
