from unittest import TestCase
from unittest.mock import Mock, patch

from fastapi.responses import JSONResponse

test_current_user = Mock()
mock_db = Mock()
mock_bt = Mock()

class TestEnvironment(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestEnvironment, self).__init__(*args, **kwargs)

    @patch('entities.Environment.Environment.getAvailableEnvironmentById')
    @patch('entities.User.User.getUserById') 
    def test_get_environment(self, getUserById, getAvailableEnvironmentById):
        # Given
        from controllers.environment import get_environment
        from entities.Environment import Environment
        from entities.User import User

        environment_id = 1 
        environment = Environment()
        environment.id = environment_id
        environment.name = "test"
        environment.path = "test"
        environment.description = "test"
        environment.is_private = False
        environment.logo_url = "test"
        environment.environment_template = "test"
        environment.doc_template = "test"
        environment.roles = "test"
        environment.subdomains = "test"
        environment.type = "vm"
        getAvailableEnvironmentById.return_value = environment
        userId = 1
        enabled_features = {
            "daasapi": True,
            "k8sapi": True
        }
        test_user = User(id= userId, enabled_features=enabled_features)
        getUserById.return_value = test_user

        #When
        result = get_environment(test_user, environment_id, mock_db)
        response_status_code = result.__dict__['status_code']
       
        #Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), '{"created_at":null,"description":"test","doc_template":"test","environment_template":"test","external_roles":null,"id":1,"instances":[],"is_private":false,"logo_url":"test","name":"test","path":"test","roles":"test","subdomains":"test","type":"vm"}')

    @patch('entities.Environment.Environment.getAllAvailableEnvironmentsByType',side_effect = lambda x,y : [])
    def test_get_environments(self,getAllAvailableEnvironmentsByType):
        # Given
        from controllers.environment import get_environments

        #When
        result = get_environments("vm", mock_db)
        response_status_code = result.__dict__['status_code']

        #Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), "[]")
