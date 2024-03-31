from unittest import TestCase
from unittest.mock import Mock, patch

from fastapi.responses import JSONResponse

test_current_user = Mock()
mock_db = Mock()
mock_bt = Mock()

class TestAdminBucket(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestAdminBucket, self).__init__(*args, **kwargs)

    @patch('entities.Bucket.Bucket.getAllBucketsByRegion', side_effect = lambda x, y, z: [])
    def test_admin_get_buckets(self, getAllBucketsByRegion):
        # Given
        from controllers.admin.admin_bucket import admin_get_buckets

        # When
        result = admin_get_buckets(test_current_user, "scaleway", "fr-par", mock_db)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), "[]")

    @patch('utils.common.generate_hash_password', side_effect = lambda p: p)
    @patch('entities.Bucket.Bucket.findById')
    def test_admin_get_bucket(self, findById, generate_hash_password):
        # Given
        from controllers.admin.admin_bucket import admin_get_bucket
        from entities.Bucket import Bucket
        from entities.User import User
        target_user = User()
        target_user.email = "username@email.com"
        target_user.id = 1
        bucket_id = 1
        bucket = Bucket()
        bucket.hash = "aabbcc"
        bucket.bucket_user_id = 1
        bucket.name = "test-bucket"
        bucket.type = "private"
        bucket.provider = "scaleway"
        bucket.region = "fr-par"
        bucket.id = bucket_id
        bucket.user = target_user
        findById.return_value = bucket

        # When
        result = admin_get_bucket(test_current_user, bucket_id, mock_db)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), '{"access_key":null,"bucket_user_id":1,"created_at":null,"endpoint":null,"hash":"aabbcc","id":1,"name":"test-bucket","provider":"scaleway","region":"fr-par","secret_key":null,"status":null,"type":"private","user_id":null,"user":{"address":null,"api_keys":[],"company_name":null,"confirmed":null,"contact_info":null,"created_at":null,"email":"username@email.com","enabled_features":null,"id":1,"instances":[],"is_admin":null,"password":null,"projects":[],"registration_number":null,"registries":[],"st_customer_id":null,"st_payment_method_id":null,"support_ticket":[],"support_ticket_logs":[]}}')    
    
    @patch('entities.Bucket.Bucket.findById')
    @patch('controllers.admin.admin_bucket.delete_bucket', side_effect = None)
    @patch('entities.Bucket.Bucket.updateStatus', side_effect = None)
    @patch('utils.common.generate_hash_password', side_effect = lambda p: p)
    def test_admin_delete_bucket(self, generate_hash_password, updateStatus, delete_bucket_mock, findById):
        # Given
        from controllers.admin.admin_bucket import admin_remove_bucket
        from entities.Bucket import Bucket
        from entities.User import User
        target_user = User()
        target_user.email = "username@email.com"
        target_user.id = 1
        bucket_id = 1
        bucket = Bucket()
        bucket.hash = "aabbcc"
        bucket.user_id = target_user.id
        bucket.name = "test-bucket"
        bucket.type = "private"
        bucket.provider = "scaleway"
        bucket.region = "fr-par"
        bucket.id = bucket_id
        bucket.user = target_user
        findById.return_value = bucket

        # When
        result = admin_remove_bucket(test_current_user, bucket_id, mock_db, mock_bt)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), '{"status":"ok","message":"bucket successfully deleted","i18n_code":"401"}')
   
    @patch('entities.User.User.getUserByEmail')
    @patch('utils.common.generate_hash_password', side_effect = lambda p: p)
    @patch('utils.dynamic_name.generate_hashed_name', side_effect = lambda p: ("aabbcc", p, "test-aabbcc"))
    @patch('controllers.admin.admin_bucket.register_bucket')
    @patch('controllers.admin.admin_bucket.create_bucket', side_effect = None)
    def test_admin_add_bucket(self, create_bucket, register_bucket, generate_hash_password, generate_hashed_name, getUserByEmail):
        # Given
        from controllers.admin.admin_bucket import admin_create_bucket
        from entities.Bucket import Bucket
        from entities.User import User
        from schemas.Bucket import BucketSchema
        target_user = User()
        target_user.email = "username@email.com"
        target_user.id = 1
        bucket_id = 1
        hash, name = ("aabbcc", "test-aabbcc")
        generate_hashed_name.return_value = hash, name
        bucket = Bucket()
        bucket.hash = hash
        bucket.name = name
        bucket.bucket_user_id = 1
        bucket.type = "private"
        bucket.provider = "scaleway"
        bucket.region = "fr-par"
        bucket.id = bucket_id
        bucket.user = target_user
        getUserByEmail.return_value = target_user
        register_bucket.return_value = bucket

        payload = BucketSchema(
            name = "test",
            type = "private",
            email = "username@email.com"
        )

        # When
        result = admin_create_bucket(test_current_user, "scaleway", "fr-par", payload, mock_db, mock_bt)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), '{"access_key":null,"bucket_user_id":1,"created_at":null,"endpoint":null,"hash":"aabbcc","id":1,"name":"test-aabbcc","provider":"scaleway","region":"fr-par","secret_key":null,"status":null,"type":"private","user_id":null}')

    @patch('entities.User.User.getUserByEmail')
    @patch('entities.Bucket.Bucket.findById')
    @patch('controllers.admin.admin_bucket.update_credentials', side_effect = None)
    @patch('entities.Bucket.Bucket.patch')
    @patch('entities.Bucket.Bucket.updateStatus', side_effect = None)
    def test_admin_update_bucket(self, updateStatus, patch, update_credentials, findById, getUserByEmail):
        # Given
        from controllers.admin.admin_bucket import admin_update_bucket
        from entities.Bucket import Bucket
        from entities.User import User
        from schemas.Bucket import BucketUpdateSchema
        target_user = User()
        target_user.email = "username@email.com"
        target_user.id = 1
        bucket_id = 1
        bucket = Bucket()
        bucket.hash = "aabbcc"
        bucket.bucket_user_id = 1
        bucket.name = "test-bucket"
        bucket.type = "private"
        bucket.provider = "scaleway"
        bucket.region = "fr-par"
        bucket.id = bucket_id
        bucket.user = target_user
        getUserByEmail.return_value = target_user
        findById.return_value = bucket

        payload = BucketUpdateSchema(
            email = "username@email.com",
            update_creds = True
        )

        # When
        result = admin_update_bucket(test_current_user, bucket_id, payload, mock_db)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), '{"status":"ok","message":"bucket successfully updated","i18n_code":"402"}')

    @patch('entities.Bucket.Bucket.findById')
    @patch('controllers.admin.admin_bucket.refresh_bucket', side_effect = None)
    @patch('entities.Bucket.Bucket.updateStatus', side_effect = None)
    def test_admin_refresh_bucket(self, updateStatus, refresh_bucket, findById):
        # Given
        from controllers.admin.admin_bucket import admin_refresh_bucket
        from entities.Bucket import Bucket
        from entities.User import User
        target_user = User()
        target_user.email = "username@email.com"
        target_user.id = 1
        bucket_id = 1
        bucket = Bucket()
        bucket.hash = "aabbcc"
        bucket.bucket_user_id = 1
        bucket.name = "test-bucket"
        bucket.type = "private"
        bucket.provider = "scaleway"
        bucket.region = "fr-par"
        bucket.id = bucket_id
        bucket.user = target_user
        findById.return_value = bucket

        # When
        result = admin_refresh_bucket(test_current_user, bucket_id, mock_db)
        response_status_code = result.__dict__['status_code']
       
        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), '{"status":"ok","message":"bucket successfully refreshed","i18n_code":"405"}')
