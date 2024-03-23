from unittest import TestCase
from unittest.mock import Mock, patch

from fastapi.responses import JSONResponse

test_current_user = Mock()
mock_db = Mock()
mock_bt = Mock()

class TestAdminRegistry(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestAdminRegistry, self).__init__(*args, **kwargs)

    @patch('entities.Registry.Registry.getAllRegistriesByRegion', side_effect = lambda x, y, z: [])
    def test_admin_get_registries(self, getAllRegistriesByRegion):
        # Given
        from controllers.admin.admin_registry import admin_get_registries

        # When
        result = admin_get_registries(test_current_user, "scaleway", "fr-par", mock_db)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), "[]")   
        self.assertEqual(getAllRegistriesByRegion.call_args[0][0], "scaleway")
        self.assertEqual(getAllRegistriesByRegion.call_args[0][1], "fr-par")

    @patch('utils.common.generate_hash_password', side_effect = lambda p: p)
    @patch('entities.Registry.Registry.findById')
    def test_admin_get_registry(self, findById, generate_hash_password):
        # Given
        from controllers.admin.admin_registry import admin_get_registry
        from entities.Registry import Registry
        from entities.User import User
        target_user = User()
        target_user.email = "username@email.com"
        target_user.id = 1
        registry_id = 1
        registry = Registry()
        registry.hash = "aabbcc"
        registry.provider = "scaleway"
        registry.region = "fr-par"
        registry.type = "private"
        registry.id = registry_id
        registry.user = target_user
        findById.return_value = registry

        # When
        result = admin_get_registry(test_current_user, registry_id, mock_db)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), '{"access_key":null,"created_at":null,"endpoint":null,"hash":"aabbcc","id":1,"name":null,"provider":"scaleway","region":"fr-par","secret_key":null,"status":null,"type":"private","user_id":null,"user":{"address":null,"api_keys":[],"buckets":[],"company_name":null,"confirmed":null,"contact_info":null,"created_at":null,"email":"username@email.com","enabled_features":null,"id":1,"instances":[],"is_admin":null,"password":null,"projects":[],"registration_number":null,"st_customer_id":null,"st_payment_method_id":null,"support_ticket":[],"support_ticket_logs":[]}}')
        self.assertEqual(findById.call_count, 1)

    @patch('entities.Registry.Registry.findById')
    @patch('controllers.admin.admin_registry.delete_registry', side_effect = None)
    @patch('entities.Registry.Registry.updateStatus', side_effect = None)
    @patch('utils.common.generate_hash_password', side_effect = lambda p: p)
    def test_admin_delete_registry(self, generate_hash_password, updateStatus, delete_registry_mock, findById):
        # Given
        from controllers.admin.admin_registry import admin_remove_registry
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
        registry.user_id = target_user.id
        findById.return_value = registry

        # When
        result = admin_remove_registry(test_current_user, registry_id, mock_db, mock_bt)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(),'{"status":"ok","message":"registry successfully deleted","i18n_code":"901"}')

    @patch('entities.User.User.getUserByEmail')
    @patch('utils.common.generate_hash_password', side_effect = lambda p: p)
    @patch('utils.bytes_generator.generate_hashed_name', side_effect = lambda p: ("aabbcc", p, "test-aabbcc"))
    @patch('controllers.admin.admin_registry.register_registry')
    @patch('controllers.admin.admin_registry.create_registry', side_effect = None)
    def test_admin_add_registry(self, create_registry, register_registry, generate_hash_password, generate_hashed_name, getUserByEmail):
        # Given
        from controllers.admin.admin_registry import admin_add_registry
        from entities.Registry import Registry
        from entities.User import User
        from schemas.Registry import RegistrySchema
        target_user = User()
        target_user.email = "username@email.com"
        target_user.id = 1
        registry_id = 1
        hash, name = ("aabbcc", "test-aabbcc")
        generate_hashed_name.return_value = hash, name
        registry = Registry()
        registry.id = registry_id
        registry.hash = "aabbcc"
        registry.provider = "scaleway"
        registry.region = "fr-par"
        registry.type = "private"
        registry.user = target_user
        getUserByEmail.return_value = target_user
        register_registry.return_value = registry

        payload = RegistrySchema(
            name = "test",
            email = "username@email",
            type = "private"
        )

        # When
        result = admin_add_registry(test_current_user, "scaleway", "fr-par", payload, mock_db, mock_bt)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)   
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), '{"access_key":null,"created_at":null,"endpoint":null,"hash":"aabbcc","id":1,"name":null,"provider":"scaleway","region":"fr-par","secret_key":null,"status":null,"type":"private","user_id":null}')

    @patch('entities.User.User.getUserByEmail')
    @patch('entities.Registry.Registry.findById')
    @patch('controllers.admin.admin_registry.update_credentials', side_effect = None)
    @patch('entities.Registry.Registry.patch')
    @patch('entities.Registry.Registry.updateStatus', side_effect = None)
    def test_admin_update_registry(self, updateStatus, patch, update_credentials, findById, getUserByEmail):
        # Given
        from controllers.admin.admin_registry import admin_update_registry
        from entities.Registry import Registry
        from entities.User import User
        from schemas.Registry import RegistryUpdateSchema
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
        getUserByEmail.return_value = target_user
        findById.return_value = registry

        payload = RegistryUpdateSchema(
            email = "username@email.com",
            update_creds = True
        )

        # When
        result = admin_update_registry(test_current_user, registry_id, payload, mock_db)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), '{"status":"ok","message":"registry successfully updated","i18n_code":"902"}')
