from unittest import TestCase
from unittest.mock import Mock, patch 
import io
from fastapi.responses import JSONResponse 
from entities.Environment import Environment
from fastapi import UploadFile
test_current_user = Mock()
mock_db = Mock()
mock_bt = Mock()

class TestAdminEnvironnement(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestAdminEnvironnement, self).__init__(*args, **kwargs)

    @patch('controllers.admin.admin_environment.get_infra_playbook_roles', side_effect = None)
    def test_admin_get_roles(self,get_infra_playbook_roles):
        # Given  
        from controllers.admin.admin_environment import admin_get_roles

        # When
        result = admin_get_roles(test_current_user)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), '{"roles":[]}') 
       
    @patch('controllers.admin.admin_environment.Environment.getById',side_effect = None)     
    def test_admin_get_environment(self, getById):
        # Given  
        from controllers.admin.admin_environment import admin_get_environment 
        from entities.Environment import Environment
        environment_id = 1
        environment = Environment()
        environment.id = environment_id
        environment.name = "test"
        environment.path = "test"
        environment.description = "test"
        environment.logo_url = "test"
        environment.environment_template = "test"
        environment.doc_template = "test"
        environment.roles = "test"
        environment.subdomains = "test"
        environment.created_at = "test"
        environment.is_private = True
        getById.return_value = environment

        # When
        result = admin_get_environment(test_current_user, 1, mock_db)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), '{"created_at":"test","description":"test","doc_template":"test","environment_template":"test","id":1,"instances":[],"is_private":true,"logo_url":"test","name":"test","path":"test","roles":"test","subdomains":"test"}')

    @patch('controllers.admin.admin_environment.Environment.getByPath',side_effect = lambda x, y: [] )
    def test_admin_add_environment(self, getByPath):
        # Given  
        from controllers.admin.admin_environment import admin_add_environment 
        from entities.Environment import Environment
        from schemas.Environment import EnvironmentSchema
        environment = Environment()
        environment.name = "test"
        environment.path = "test"
        environment.roles = "test"
        environment.subdomains = "test"
        environment.description = "test"
        environment.logo_url = "test"
        environment.environment_template = "test"
        environment.doc_template = "test"
        getByPath.return_value = None

        payload = EnvironmentSchema(
            name = "test",
            path = "test",
            description = "test",
            environment_template = "test",
            doc_template = "test",
            roles = ["test"],
            subdomains = ["test"],
            is_private= True,
            logo_url = "test"
        )

        # When
        result = admin_add_environment(test_current_user, payload, mock_db)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 201)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), '{"created_at":null,"description":"test","doc_template":"test","environment_template":"test","id":null,"instances":[],"is_private":true,"logo_url":"test","name":"test","path":"test","roles":"test","subdomains":"test"}')

    @patch('controllers.admin.admin_environment.Environment.getAll',side_effect = lambda x: [])
    def test_admin_get_all_environments(self, getAll):
        # Given  
        from controllers.admin.admin_environment import admin_get_environments 
        from entities.Environment import Environment
        environment = Environment()
        environment.id = 1
        environment.name = "test"
        environment.path = "test"
        environment.path = "test"
        environment.description = "test"
        environment.logo_url = "test"
        environment.environment_template = "test"
        environment.doc_template = "test"
        environment.roles = "test"
        getAll.return_value = environment

        # When
        result = admin_get_environments(test_current_user, mock_db)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)  
        self.assertIsInstance(result, JSONResponse)          
        self.assertEqual(result.body.decode(), "[]")
    
    @patch('controllers.admin.admin_environment.Environment.deleteOne',side_effect = lambda x, y: [])    
    def test_admin_remove_environment(self,deleteOne):
        # Given  
        from controllers.admin.admin_environment import admin_remove_environment
        from entities.Environment import Environment
        environment = Environment()
        environment.id = 1
        environment.name = "test"
        environment.path = "test"
        environment.path = "test"
        environment.description = "test"
        environment.logo_url = "test"
        environment.environment_template = "test"
        environment.doc_template = "test"
        environment.roles = "test"
        deleteOne.return_value = environment

        # When
        result = admin_remove_environment(test_current_user, 1, mock_db)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)     
        self.assertEqual(result.body.decode(),'{"message":"Environment successfully deleted","i18n_code":"802"}')
    
    @patch('controllers.admin.admin_environment.Environment.updateEnvironment', side_effect = None)      
    def test_admin_update_environment(self, updateEnvironment):
        # Given  
        from controllers.admin.admin_environment import admin_update_environment
        from entities.Environment import Environment
        from schemas.Environment import EnvironmentSchema
        environment = Environment()
        environment.id = 1  
        environment.name = "name"
        environment.path = "path"
        environment.description = "description"
        environment.roles = "roles"
        environment.subdomains = "subdomains"
        environment.environment_template = "environment_template"
        environment.doc_template = "doc_template"
        environment.is_private = True       
        updateEnvironment.return_.value = environment

        environmentId = 1
        payload = EnvironmentSchema(
            name = "test",
            path = "test",
            description = "test",
            environment_template = "test",
            doc_template = "test",
            roles = ["test"],
            subdomains = ["test"],
            is_private= True,
            logo_url = "test"
        )

        # When
        result = admin_update_environment(test_current_user, environmentId , payload, mock_db)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)       
        self.assertIsInstance(result, JSONResponse)      
        self.assertEqual(result.body.decode(), '{"message":"environment successfully updated","i18n_code":"801"}')

    @patch('controllers.admin.admin_environment.json.loads', return_value={"name": "Test Environment", "path": "test", "description": "Test Description", "roles": [], "subdomains": [], "environment_template": "template", "doc_template": "template", "is_private": False})    
    @patch('controllers.admin.admin_environment.Environment.getByPath', side_effect = lambda x, y: [])
    @patch('entities.Environment.Environment.save')
    def test_admin_import_environment(self, json, getByPath, save):
        # Given
        from controllers.admin.admin_environment import admin_import_environment 
        from entities.Environment import Environment 
        env_string = '{"name": "Test Environment", "path": "test", "description": "Test Description", "roles": [], "subdomains": [], "environment_template": "template", "doc_template": "template", "is_private": False}'
        env_file = UploadFile(filename="test.json", file=io.BytesIO(env_string.encode()))
        getByPath.return_value = None
 
        # When
        result = admin_import_environment(test_current_user, env_file , mock_db)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
    
    @patch('utils.common.is_numeric')
    @patch('entities.Environment.Environment.getById', side_effect = lambda x, y: Environment())
    def test_admin_export_environment(self, is_numeric, getById):
        # Given
        from controllers.admin.admin_environment import admin_export_environment 
        from entities.Environment import Environment 
        environment_id = 1
        environment = Environment()
        environment.id = environment_id
        environment.name = "name"
        environment.path = "path"
        getById.return_value = environment
 
        # When
        result = admin_export_environment(test_current_user, environment_id , mock_db)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), '{"file_name":"environment-None.json","blob":"ewogICAgImNyZWF0ZWRfYXQiOiBudWxsLAogICAgImRlc2NyaXB0aW9uIjogbnVsbCwKICAgICJkb2NfdGVtcGxhdGUiOiBudWxsLAogICAgImVudmlyb25tZW50X3RlbXBsYXRlIjogbnVsbCwKICAgICJpZCI6IG51bGwsCiAgICAiaW5zdGFuY2VzIjogW10sCiAgICAiaXNfcHJpdmF0ZSI6IG51bGwsCiAgICAibG9nb191cmwiOiBudWxsLAogICAgIm5hbWUiOiBudWxsLAogICAgInBhdGgiOiBudWxsLAogICAgInJvbGVzIjogbnVsbCwKICAgICJzdWJkb21haW5zIjogbnVsbAp9"}')
