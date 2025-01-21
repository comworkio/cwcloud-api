from unittest import TestCase
from unittest.mock import Mock, patch

from fastapi.responses import JSONResponse

test_current_user = Mock()
mock_db = Mock()
mock_bt = Mock()

class TestBucket(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestBucket, self).__init__(*args, **kwargs)

    @patch('entities.Access.Access.getUserAccessesByType', side_effect = lambda x, y, z: [])
    @patch('entities.Bucket.Bucket.findBucketsByRegion', side_effect = lambda x, y, z, w: [])
    @patch('entities.Bucket.Bucket.getAllUserBucketsByRegion', side_effect = lambda x, y, z, w: [])
    def test_get_buckets(self, getAllUserBucketsByRegion, findBucketsByRegion, getUserAccessesByType):
        # Given
        from controllers.bucket import get_buckets

        # When
        result = get_buckets(test_current_user, "scaleway", "fr-par", mock_db)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), "[]")

    @patch('entities.Bucket.Bucket.findUserBucket')
    def test_get_bucket(self, findUserBucket):
        # Given
        from controllers.bucket import get_bucket
        from entities.Bucket import Bucket
        bucket_id = 1

        bucket = Bucket()
        bucket.hash = "aabbcc"
        bucket.bucket_user_id = 1
        bucket.name = "test-bucket"
        bucket.type = "private"
        bucket.provider = "scaleway"
        bucket.region = "fr-par"
        bucket.id = bucket_id
        findUserBucket.return_value = bucket

        # When
        result = get_bucket(test_current_user, "scaleway", "fr-par", bucket_id, mock_db)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.maxDiff = None
        import json
        actual_json = json.loads(result.body.decode())
        expected_json = {
            "access_key": None,
            "bucket_user_id": 1,
            "created_at": None,
            "endpoint": None,
            "hash": "aabbcc",
            "id": 1,
            "name": "test-bucket",
            "provider": "scaleway",
            "region": "fr-par",
            "secret_key": None,
            "status": None,
            "type": "private",
            "user": None,
            "user_id": None
        }
        self.assertEqual(actual_json, expected_json)

    @patch('entities.Bucket.Bucket.findUserBucket')
    @patch('controllers.bucket.delete_bucket', side_effect = None)
    @patch('entities.Bucket.Bucket.updateStatus', side_effect = None)
    def test_delete_bucket(self, updateStatus, delete_bucket_mock, findUserBucket):
        # Given
        from controllers.bucket import remove_bucket
        from entities.Bucket import Bucket
        from entities.User import User
        target_user = User()
        target_user.email = "username@gmail.com"
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
        bucket.id = bucket_id
        bucket.user = target_user
        findUserBucket.return_value = bucket

        # When
        result = remove_bucket(test_current_user, "scaleway", "fr-par", bucket_id, mock_db, mock_bt)
        response_status_code = result.__dict__['status_code']

        # Then
        self.assertIsNotNone(result)
        self.assertEqual(response_status_code, 200)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.body.decode(), '{"status":"ok","message":"bucket successfully deleted","i18n_code":"bucket_deleted"}')
