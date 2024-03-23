from unittest import TestCase
from unittest.mock import Mock, patch

from fastapi.responses import JSONResponse

test_current_user = Mock()
mock_db = Mock()
mock_bt = Mock()

class TestInstance(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestInstance, self).__init__(*args, **kwargs)
    @patch('entities.Access.Access.getUserAccessesByType', side_effect = lambda x, y, z: [])
    @patch('entities.Instance.Instance.findInstancesByRegion', side_effect = lambda x, y, z, w: [])
    @patch('entities.Instance.Instance.getActiveUserInstancesPerRegion', side_effect = lambda x, y, z, w: [])
    def test_get_instances(self, getActiveUserInstancesPerRegion, findInstancesByRegion, getUserAccessesByType):
        # Given
        from controllers.instance import get_instances

        # When
        result = get_instances(test_current_user, "scaleway", "fr-par", mock_db)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), "[]")

    @patch('entities.Instance.Instance.findUserInstance')
    def test_get_instance(self, findUserInstance):
        # Given
        from controllers.instance import get_instance
        from entities.Instance import Instance
        from entities.Environment import Environment
        from entities.Project import Project
        instance_id = 1
        instance = Instance()
        instance.hash = "aabbcc"
        instance.name = "test-instance"
        instance.type = "DEV1-S"
        instance.user_id = 1
        instance.provider = "scaleway"
        instance.region = "fr-par"
        instance.zone = "comwork.cloud"
        instance.status = "active"
        instance.ip_address = "0.0.0.0"
        instance.id = instance_id

        environment = Environment()
        environment.name = "test_environment"
        environment.path = "environemnt_path"
        environment.description = "test_description"
        environment.is_private = False
        environment.logo_url = "https://whatever.com/logo.png"
        environment.environment_template = "test_template"
        environment.doc_template = "test_doc_template"
        environment.roles = "role1"
        environment.subdomains = "comwork.cloud"
        environment.id = 1

        project = Project()
        project.name = "test_project"
        project.url = "https://gitlab.comwork.io/dynamic/test_project"
        project.user_id = 1
        project.gitlab_url = "https://gitlab.comwork.io"
        project.gitlab_username = "amirghedira"
        project.gitlab_token = "TOKEN"
        project.gitlab_project_id = "1"
        project.type = "vm"
        project.id = 1

        instance.environment = environment
        instance.project = project

        instance.environment_id = environment.id
        instance.project_id = project.id

        findUserInstance.return_value = instance

        # When
        result = get_instance(test_current_user, "scaleway", "fr-par", instance_id, mock_db)
        response_status_code = result.__dict__['status_code']
       
        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), '{"consumptions":[],"created_at":null,"environment_id":1,"hash":"aabbcc","id":1,"ip_address":"0.0.0.0","modification_date":null,"name":"test-instance","project_id":1,"provider":"scaleway","region":"fr-par","root_dns_zone":null,"status":"active","type":"DEV1-S","user":null,"user_id":1,"zone":"comwork.cloud","environment":"test_environment","path":"environemnt_path","project":{"access_token":null,"created_at":null,"git_username":null,"gitlab_host":null,"gitlab_project_id":"1","gitlab_token":"TOKEN","gitlab_url":"https://gitlab.comwork.io","gitlab_username":"amirghedira","id":1,"name":"test_project","namespace_id":null,"type":"vm","url":"https://gitlab.comwork.io/dynamic/test_project","user":null,"user_id":1,"userid":null}}')
    
    @patch('utils.bytes_generator.generate_hashed_name', side_effect = lambda p: ("aabbcc", p, "test-aabbcc"))
    @patch('entities.User.User.getUserById')
    @patch('entities.Environment.Environment.getByPath')
    @patch('controllers.instance.get_project_quietly', side_effect = lambda e: {'id': 1})
    @patch('controllers.instance.get_user_project_by_id')
    @patch('controllers.instance.register_instance')
    @patch('controllers.instance.create_instance', side_effect = lambda provider, ami_image, instance_id, user_email, instance_name, hashed_instance_name, environment, instance_region, instance_zone, generate_dns, gitlab_project, user_project, instance_type, debug, centralized, root_dns_zone, db : "")
    @patch('utils.gitlab.get_gitlab_project_tree', side_effect = lambda x, y, z: [])
    @patch('controllers.instance.check_exist_instance', side_effect = lambda userid, instance_name, db: False)
    def test_create_instance(self, check_exist_instance, get_gitlab_project_tree, create_instance, register_instance, get_user_project_by_id, get_gitlab_project, getByPath, getUserById, generate_hashed_name):
        # Given
        from controllers.instance import provision_instance
        from entities.Environment import Environment
        from entities.Instance import Instance
        from entities.Project import Project
        from entities.User import User
        from schemas.Instance import InstanceProvisionSchema
        target_user = User()
        target_user.email = "username@gmail.com"
        target_user.id = 1
        target_user.enabled_features = {}
        target_user.enabled_features['billable'] = True
        getUserById.return_value = target_user
        get_gitlab_project.return_value = {"id": 1, "name": "test_project", "gitlab_url": "https://gitlab.comwork.io/dynamic/test_project", "userid": "1", "gitlab_host": "https://gitlab.comwork.io", "access_token": "testingTOKEN", "namespace_id": "1"}
        project = Project()
        project.name = "test_project"
        project.url = "https://gitlab.comwork.io/dynamic/test_project"
        project.user_id = 1
        project.gitlab_url = "https://gitlab.comwork.io"
        project.gitlab_username = "amirghedira"
        project.gitlab_token = "TOKEN"
        project.gitlab_project_id = "1"
        project.id = 1
        get_user_project_by_id.return_value = project
        environment = Environment()
        environment.name = "code"
        environment.path = "code"
        environment.description = "code environment"
        environment.is_private = False
        environment.logo_url = "https://whatever.com/logo.png"
        environment.environment_template = ""
        environment.doc_template = ""
        environment.roles = "code"
        environment.subdomains = "comwork.cloud"
        environment.id = 1
        getByPath.return_value = environment
        instance_id = 1
        hash, name = ("aabbcc", "test-aabbcc")
        generate_hashed_name.return_value = hash, name
        new_instance = Instance()
        new_instance.hash = hash
        new_instance.name = name
        new_instance.type = "DEV1-S"
        new_instance.provider = "scaleway"
        new_instance.region = "fr-par"
        new_instance.zone = "1"
        new_instance.status = "deleted"
        new_instance.root_dns_zone = "comwork.cloud"
        new_instance.user_id = 1
        new_instance.id = instance_id
        new_instance.environment = environment
        new_instance.project = project
        register_instance.return_value = new_instance

        payload = InstanceProvisionSchema(
            name = "test",
            type = "DEV1-S",
            root_dns_zone = "comwork.cloud",
            debug = True,
            email = "test@gmail.com",
            project_id = "1",
        )

        # When
        result = provision_instance(test_current_user, payload, "scaleway", "fr-par", "1", "code", mock_db, mock_bt)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), '{"consumptions":[],"created_at":null,"environment_id":null,"hash":"aabbcc","id":1,"ip_address":null,"modification_date":null,"name":"test-aabbcc","project_id":null,"provider":"scaleway","region":"fr-par","root_dns_zone":"comwork.cloud","status":"deleted","type":"DEV1-S","user":null,"user_id":1,"zone":"1","environment":"code","path":"code","gitlab_project":"https://gitlab.comwork.io/dynamic/test_project"}')
    
    @patch('entities.User.User.getUserById')
    @patch('controllers.instance.get_gitlab_project')
    @patch('controllers.instance.get_user_project_by_id')
    @patch('controllers.instance.reregister_instance')
    @patch('controllers.instance.get_gitlab_project_playbooks', side_effect = lambda x, y, z: ["playbook-test-instance"])
    @patch('controllers.instance.check_exist_instance', side_effect = lambda userid, instance_name: False)
    @patch('entities.Instance.Instance.findUserInstanceByName')
    @patch('entities.Environment.Environment.getById')
    def test_attach_instance(self, getById, findUserInstanceByName, check_exist_instance, get_gitlab_project_tree, reregister_instance, get_user_project_by_id, get_gitlab_project, getUserById):
        # Given
        from controllers.instance import attach_instance
        from entities.Environment import Environment
        from entities.Instance import Instance
        from entities.Project import Project
        from entities.User import User
        from schemas.Instance import InstanceAttachSchema
        target_user = User()
        target_user.email = "username@email.com"
        target_user.id = 1
        target_user.enabled_features = {}
        target_user.enabled_features['billable'] = True
        getUserById.return_value = target_user
        get_gitlab_project.return_value = {"id": 1, "name": "test_project", "gitlab_url": "https://gitlab.comwork.io/dynamic/test_project", "userid": "1", "gitlab_host": "https://gitlab.comwork.io", "access_token": "testingTOKEN", "namespace_id": "1"}
        project = Project()
        project.name = "test_project"
        project.url = "https://gitlab.comwork.io/dynamic/test_project"
        project.user_id = 1
        project.gitlab_url = "https://gitlab.comwork.io"
        project.gitlab_username = "amirghedira"
        project.gitlab_token = "TOKEN"
        project.gitlab_project_id = "1"
        project.id = 1
        get_user_project_by_id.return_value = project

        environment = Environment()
        environment.name = "code"
        environment.path = "code"
        environment.description = "code environment"
        environment.is_private = False
        environment.logo_url = "https://whatever.com/logo.png"
        environment.environment_template = ""
        environment.doc_template = ""
        environment.roles = "code"
        environment.subdomains = "comwork.cloud"
        environment.id = 1

        old_instance = Instance()
        old_instance.hash = "aabbcc"
        old_instance.name = "test-instance"
        old_instance.type = "DEV1-S"
        old_instance.provider = "scaleway"
        old_instance.region = "fr-par"
        old_instance.zone = "1"
        old_instance.status = "deleted"
        old_instance.root_dns_zone = "comwork.cloud"
        old_instance.user_id = 1
        old_instance.id = 1
        old_instance.environment = environment
        old_instance.project = project
        reregister_instance.return_value = old_instance
        findUserInstanceByName.return_value = old_instance
        getById.return_value = environment

        payload = InstanceAttachSchema(
            name = "test-instance",
            type = "DEV1-S",
            debug = True
        )

        # When
        result = attach_instance(mock_bt, test_current_user, "scaleway", "fr-par", "1", 1, payload, mock_db)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), '{"consumptions":[],"created_at":null,"environment_id":null,"hash":"aabbcc","id":1,"ip_address":null,"modification_date":null,"name":"test-instance","project_id":null,"provider":"scaleway","region":"fr-par","root_dns_zone":"comwork.cloud","status":"deleted","type":"DEV1-S","user":null,"user_id":1,"zone":"1","environment":"code","path":"code","gitlab_project":"https://gitlab.comwork.io/dynamic/test_project"}')
