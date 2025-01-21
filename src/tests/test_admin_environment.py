import io

from unittest import TestCase
from unittest.mock import Mock, patch 

from fastapi.responses import JSONResponse 
from fastapi import UploadFile

from entities.Environment import Environment

test_current_user = Mock()
mock_db = Mock()
mock_bt = Mock()

class TestAdminEnvironnement(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestAdminEnvironnement, self).__init__(*args, **kwargs)

    @patch('controllers.admin.admin_environment.get_infra_playbook_roles', side_effect = None)
    def test_admin_get_roles(self, get_infra_playbook_roles):
        # Given  
        from controllers.admin.admin_environment import admin_get_roles
        get_infra_playbook_roles.return_value = None, []

        # When
        result = admin_get_roles(test_current_user)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), '{"roles":[]}') 
       
    @patch('controllers.admin.admin_environment.Environment.getById', side_effect=None)
    def test_admin_get_environment(self, getById):
        # Given
        from controllers.admin.admin_environment import admin_get_environment
        from entities.Environment import Environment
        import json

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
        environment.type = "vm"
        environment.is_private = True
        getById.return_value = environment

        expected_json = {
            "args": None,
            "created_at": "test",
            "description": "test",
            "doc_template": "test",
            "environment_template": "test",
            "external_roles": None,
            "id": 1,
            "instances": [],
            "is_private": True,
            "logo_url": "test",
            "name": "test",
            "path": "test",
            "roles": "test",
            "subdomains": "test",
            "type": "vm",
        }

        # When
        result = admin_get_environment(environment_id, mock_db)
        response_status_code = result.__dict__["status_code"]

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)

        actual_json = json.loads(result.body.decode())
        self.maxDiff = None
        self.assertEqual(actual_json, expected_json)

    @patch('controllers.admin.admin_environment.Environment.getByPath', side_effect=lambda x, y: [])
    def test_admin_add_environment(self, getByPath):
        # Given  
        from controllers.admin.admin_environment import admin_add_environment
        from entities.Environment import Environment
        from schemas.Environment import EnvironmentSchema
        import json

        environment = Environment()
        environment.name = "test"
        environment.path = "test"
        environment.roles = "test"
        environment.subdomains = "test"
        environment.description = "test"
        environment.logo_url = "test"
        environment.environment_template = "test"
        environment.doc_template = "test"
        environment.type = "vm"
        getByPath.return_value = None

        payload = EnvironmentSchema(
            name="test",
            path="test",
            description="test",
            environment_template="test",
            doc_template="test",
            roles=["test"],
            subdomains=["test"],
            is_private=True,
            logo_url="test"
        )

        expected_response = {
            "args": "[]",
            "created_at": None,
            "description": "test",
            "doc_template": "test",
            "environment_template": "test",
            "external_roles": None,
            "id": None,
            "instances": [],
            "is_private": True,
            "logo_url": "test",
            "name": "test",
            "path": "test",
            "roles": "test",
            "subdomains": "test",
            "type": "vm"
        }

        # When
        result = admin_add_environment(payload, mock_db)
        response_status_code = result.__dict__["status_code"]

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 201)
        self.assertIsInstance(result, JSONResponse)

        actual_response = json.loads(result.body.decode())
        self.maxDiff = None
        self.assertEqual(actual_response, expected_response)

    @patch('controllers.admin.admin_environment.Environment.getByType',side_effect = lambda x,y: [])
    def test_admin_get_all_environments(self, getByType):
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
        environment.type = "vm"
        getByType.return_value = environment

        # When
        result = admin_get_environments("vm",None,None, mock_db)
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
        environment.type = "vm"
        deleteOne.return_value = environment

        # When
        result = admin_remove_environment(1, mock_db)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)     
        self.assertEqual(result.body.decode(),'{"status":"ok","message":"Environment successfully deleted","i18n_code":"environment_deleted"}')
    
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
        environment.type = "vm"
        updateEnvironment.return_.value = environment

        environment_id = 1
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
        result = admin_update_environment(environment_id, payload, mock_db)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)       
        self.assertIsInstance(result, JSONResponse)      
        self.assertEqual(result.body.decode(), '{"status":"ok","message":"environment successfully updated","i18n_code":"environment_updated"}')

    @patch('controllers.admin.admin_environment.json.loads', return_value={"name": "Test Environment", "path": "test", "description": "Test Description", "roles": [], "subdomains": [], "environment_template": "template", "doc_template": "template", "is_private": False, "type": "vm"})    
    @patch('controllers.admin.admin_environment.Environment.getByPath', side_effect = lambda x, y: [])
    @patch('entities.Environment.Environment.save')
    def test_admin_import_environment(self, json, getByPath, save):
        # Given
        from controllers.admin.admin_environment import admin_import_environment 
        env_string = '{"name": "Test Environment", "path": "test", "description": "Test Description", "roles": [], "subdomains": [], "environment_template": "template", "doc_template": "template", "is_private": False, "type": "vm"}'
        env_file = UploadFile(filename="test.json", file=io.BytesIO(env_string.encode()))
        getByPath.return_value = None
 
        # When
        result = admin_import_environment(env_file , mock_db)
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
        self.assertEqual(result.body.decode(), '{"status":"ok","file_name":"environment-None.json","blob":"ewogICAgImFyZ3MiOiBudWxsLAogICAgImNyZWF0ZWRfYXQiOiBudWxsLAogICAgImRlc2NyaXB0aW9uIjogbnVsbCwKICAgICJkb2NfdGVtcGxhdGUiOiBudWxsLAogICAgImVudmlyb25tZW50X3RlbXBsYXRlIjogbnVsbCwKICAgICJleHRlcm5hbF9yb2xlcyI6IG51bGwsCiAgICAiaWQiOiBudWxsLAogICAgImluc3RhbmNlcyI6IFtdLAogICAgImlzX3ByaXZhdGUiOiBudWxsLAogICAgImxvZ29fdXJsIjogbnVsbCwKICAgICJuYW1lIjogbnVsbCwKICAgICJwYXRoIjogbnVsbCwKICAgICJyb2xlcyI6IG51bGwsCiAgICAic3ViZG9tYWlucyI6IG51bGwsCiAgICAidHlwZSI6IG51bGwKfQ=="}')
