from unittest import TestCase
from unittest.mock import Mock, patch

from fastapi.responses import JSONResponse

test_current_user = Mock()
mock_db = Mock()
mock_bt = Mock()

class TestRegistry(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestRegistry, self).__init__(*args, **kwargs)
    @patch('entities.Access.Access.getUserAccessesByType', side_effect = lambda x, y, w: [])
    @patch('entities.Registry.Registry.findRegistriesByRegion', side_effect = lambda x, y, z, w: [])
    @patch('entities.Registry.Registry.getAllUserRegistriesByRegion', side_effect = lambda x, y, z, w: [])
    def test_get_registries(self, getAllUserRegistriesByRegion, findRegistriesByRegion, getUserAccessesByType):
        # Given
        from controllers.registry import get_registries

        # When
        result = get_registries(test_current_user, "scaleway", "fr-par", mock_db)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), "[]")

    @patch('entities.Registry.Registry.findUserRegistry')
    def test_get_registry(self, findUserRegistry):
        # Given
        from controllers.registry import get_registry
        from entities.Registry import Registry
        registry_id = 1
        registry = Registry()
        registry.id = registry_id
        registry.hash = "aabbcc"
        registry.provider = "scaleway"
        registry.region = "fr-par"
        registry.type = "private"
        findUserRegistry.return_value = registry

        # When
        result = get_registry(test_current_user, "scaleway", "fr-par", registry_id, mock_db)
        response_status_code = result.__dict__['status_code']
       
        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), '{"access_key":null,"created_at":null,"endpoint":null,"hash":"aabbcc","id":1,"name":null,"provider":"scaleway","region":"fr-par","secret_key":null,"status":null,"type":"private","user":null,"user_id":null}')

    @patch('entities.Registry.Registry.findUserRegistry')
    @patch('controllers.registry.delete_registry', side_effect = None)
    @patch('entities.Registry.Registry.updateStatus', side_effect = None)
    def test_delete_registry(self, updateStatus, delete_registry, findUserRegistry):
        # Given
        from controllers.registry import remove_registry
        from entities.Registry import Registry
        from entities.User import User
        target_user = User()
        target_user.email = "username@email.com"
        target_user.id = 1
        registry_id = 1
        registry = Registry()
        registry.id = registry_id
        registry.hash = "aabbcc"
        registry.provider = "scaleway"
        registry.region = "fr-par"
        registry.type = "private"
        registry.user = target_user
        findUserRegistry.return_value = registry

        # When
        result = remove_registry(test_current_user, "scaleway", "fr-par", registry_id, mock_db, mock_bt)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), '{"status":"ok","message":"registry successfully deleted","i18n_code":"902"}')
    