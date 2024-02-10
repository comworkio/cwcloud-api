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
    def test_get_environment(self,getAvailableEnvironmentById):
        # Given
        from controllers.environment import get_environment
        from entities.Environment import Environment

        environmentId = 1 
        environment = Environment()
        environment.id = environmentId
        environment.name = "test"
        environment.path = "test"
        environment.description = "test"
        environment.is_private = False
        environment.logo_url = "test"
        environment.environment_template = "test"
        environment.doc_template = "test"
        environment.roles = "test"
        environment.subdomains = "test"
        getAvailableEnvironmentById.return_value = environment

        #When
        result = get_environment(test_current_user,environmentId, mock_db)
        response_status_code = result.__dict__['status_code']
       
        #Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)    
        self.assertEqual(result.body.decode(), '{"created_at":null,"description":"test","doc_template":"test","environment_template":"test","id":1,"instances":[],"is_private":false,"logo_url":"test","name":"test","path":"test","roles":"test","subdomains":"test"}')

    @patch('entities.Environment.Environment.getAllAvailableEnvironments',side_effect = lambda x : [])
    def test_get_environments(self,getAllAvailableEnvironments):
        # Given
        from controllers.environment import get_environments

        #When
        result = get_environments(test_current_user, mock_db)
        response_status_code = result.__dict__['status_code']

        #Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), "[]")
