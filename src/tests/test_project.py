from unittest import TestCase
from unittest.mock import Mock, patch
from fastapi.responses import JSONResponse

test_current_user = Mock()
mock_db = Mock()
class TestProject(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestProject, self).__init__(*args, **kwargs)
    @patch('entities.Access.Access.getUserAccessesByType', side_effect = lambda x, y, z: [])
    @patch('entities.Project.Project.findProjects', side_effect = lambda x, y: [])
    @patch('entities.Project.Project.getUserProjects', side_effect = lambda x, y : [])
    @patch('entities.Instance.Instance.getActiveUserInstances', side_effect = lambda x, y : [])
    def test_get_projects(self, getUserProjects, getActiveUserInstances, findProjects, getUserAccessesByType):
        # Given
        from controllers.project import get_projects

        # When
        result = get_projects(test_current_user, mock_db)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), "[]")

    @patch('entities.Project.Project.save')
    @patch('middleware.auth_guard.is_mock_test', side_effect = lambda: True)
    @patch('middleware.auth_guard.get_current_active_user', side_effect = lambda x: test_current_user)
    @patch('utils.common.generate_hash_password', side_effect = lambda p: p)
    @patch('utils.gitlab.create_gitlab_project')
    def test_add_project(self, create_gitlab_project_mock, generate_hash_password, get_current_active_user, is_mock_test, project_save_mock):
        # Given
        from entities.User import User
        from controllers.project import add_project
        from entities.Project import Project
        from schemas.Project import ProjectSchema
        target_user = User()
        target_user.email = "username@email.com"
        target_user.id = 1
        project_id = 1
        project_name = "test_project"
        new_project = Project()
        new_project.id = project_id
        new_project.name = project_name
        new_project.url = "https://gitlab.comwork.io/dynamic/test_project"
        new_project.user_id = target_user.id
        new_project.gitlab_url = "https://gitlab.comwork.io"
        new_project.gitlab_username = "amirghedira"
        new_project.gitlab_token = "TOKEN"
        new_project.gitlab_project_id = "1"
        new_project.type = "vm"
        create_gitlab_project_mock.return_value = new_project

        payload = ProjectSchema(
            name = project_name,
            type = "vm",
        )

        # When
        result = add_project(test_current_user, payload, mock_db)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 201)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), '{"access_token":null,"created_at":null,"git_username":null,"gitlab_host":null,"gitlab_project_id":"1","gitlab_token":"TOKEN","gitlab_url":"https://gitlab.comwork.io","gitlab_username":"amirghedira","id":1,"instances":[],"name":"test_project","namespace_id":null,"type":"vm","url":"https://gitlab.comwork.io/dynamic/test_project","user":null,"user_id":1,"userid":null}')

    @patch('entities.Project.Project.getUserProject')
    @patch('utils.gitlab.get_gitlab_project_tree', side_effect = lambda x, y, z: [])
    def test_get_project(self, get_gitlab_project_playbooks, getUserProject):
        # Given
        from controllers.project import get_project
        from entities.Project import Project
        project_id = 1
        project = Project()
        project.id = project_id
        project.name = "test_project"
        project.url = "https://gitlab.comwork.io/dynamic/test_project"
        project.user_id = 1
        project.gitlab_url = "https://gitlab.comwork.io"
        project.gitlab_username = "amirghedira"
        project.gitlab_token = "TOKEN"
        project.gitlab_project_id = "1"
        project.type = "vm"
        getUserProject.return_value = project

        # When
        result = get_project(test_current_user, project_id, mock_db)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), '{"access_token":null,"created_at":null,"git_username":null,"gitlab_host":null,"gitlab_project_id":"1","gitlab_token":"TOKEN","gitlab_url":"https://gitlab.comwork.io","gitlab_username":"amirghedira","id":1,"instances":[],"name":"test_project","namespace_id":null,"type":"vm","url":"https://gitlab.comwork.io/dynamic/test_project","user":null,"user_id":1,"userid":null,"playbooks":[]}')

    @patch('controllers.project.delete_gitlab_project', side_effect = lambda x, y, z : "" )
    @patch('entities.Project.Project.deleteOne', side_effect = lambda x, y : "" )
    @patch('entities.Project.Project.getUserProject')
    @patch('entities.Instance.Instance.getAllActiveInstancesByProject', side_effect = lambda x, y : [])
    def test_delete_project(self, getAllActiveInstancesByProject, getUserProject, deleteOne, delete_gitlab_project):
        # Given
        from controllers.project import delete_project
        from entities.Project import Project
        project_id = 1
        project = Project()
        project.id = project_id
        project.name = "test_project"
        project.url = "https://gitlab.comwork.io/dynamic/test_project"
        project.user_id = 1
        project.gitlab_url = "https://gitlab.comwork.io"
        project.gitlab_username = "amirghedira"
        project.gitlab_token = "TOKEN"
        project.gitlab_project_id = "1"
        getUserProject.return_value = project

        # When
        result = delete_project(test_current_user, project_id, mock_db)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), '{"message":"project successfully deleted","i18n_code":"202"}')
