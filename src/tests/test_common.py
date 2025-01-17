import os
import base64

from unittest import TestCase
from unittest.mock import Mock
from unittest.mock import patch

from utils.common import generate_hash_password, verify_password, is_boolean, is_not_empty, is_true, is_empty_key, del_key_if_exists, is_numeric, is_disabled, safe_compare_entry, safe_get_entry, is_response_ok, unbase64, is_uuid, to_camel_case, convert_dict_keys_to_camel_case, get_admin_status, get_env_int, sanitize_metric_name, sanitize_header_name, is_http_status_code

class TestCommonUtils(TestCase):
    def test_verify_password(self):
        hashed = generate_hash_password("test123")
        self.assertTrue(verify_password("test123", hashed))
        self.assertFalse(verify_password("wrong", hashed))

    def test_is_boolean(self):
        self.assertTrue(is_boolean(True))
        self.assertTrue(is_boolean("true"))
        self.assertTrue(is_boolean("false"))
        self.assertTrue(is_boolean("yes"))
        self.assertFalse(is_boolean("other"))

    def test_is_not_empty(self):
        self.assertTrue(is_not_empty(True))
        self.assertTrue(is_not_empty(1))
        self.assertTrue(is_not_empty([1]))
        self.assertTrue(is_not_empty({"key": "value"}))
        self.assertFalse(is_not_empty(""))
        self.assertFalse(is_not_empty("null"))
        self.assertFalse(is_not_empty(None))

    def test_is_true(self):
        self.assertTrue(is_true(True))
        self.assertTrue(is_true("yes"))
        self.assertFalse(is_true("false"))
        self.assertFalse(is_true("no"))

    def test_is_empty_key(self):
        test_dict = {"exists": "value", "empty": ""}
        self.assertTrue(is_empty_key(test_dict, "missing"))
        self.assertTrue(is_empty_key(test_dict, "empty"))
        self.assertFalse(is_empty_key(test_dict, "exists"))

    def test_del_key_if_exists(self):
        test_dict = {"key": "value"}
        del_key_if_exists(test_dict, "key")
        self.assertNotIn("key", test_dict)

    def test_is_numeric(self):
        self.assertTrue(is_numeric(123))
        self.assertTrue(is_numeric("123"))
        self.assertFalse(is_numeric("abc"))

    def test_is_disabled(self):
        self.assertTrue(is_disabled("changeit"))
        self.assertTrue(is_disabled(""))
        self.assertFalse(is_disabled("enabled"))

    def test_safe_compare_entry(self):
        test_dict = {"key": "value"}
        self.assertTrue(safe_compare_entry(test_dict, "key", "value"))
        self.assertFalse(safe_compare_entry(test_dict, "key", "wrong"))
        self.assertFalse(safe_compare_entry(test_dict, "missing", "value"))

    def test_safe_get_entry(self):
        test_dict = {"key": "value"}
        self.assertEqual(safe_get_entry(test_dict, "key"), "value")
        self.assertEqual(safe_get_entry(test_dict, "missing", "default"), "default")

    def test_is_response_ok(self):
        self.assertTrue(is_response_ok(200))
        self.assertTrue(is_response_ok(299))
        self.assertFalse(is_response_ok(400))

    def test_unbase64(self):
        encoded = base64.b64encode("test".encode('utf-8'))
        self.assertEqual(unbase64(encoded), "test")

    def test_is_uuid(self):
        valid_uuid = "123e4567-e89b-4123-8456-426614174000"
        invalid_uuid = "not-a-uuid"
        self.assertTrue(is_uuid(valid_uuid))
        self.assertFalse(is_uuid(invalid_uuid))

    def test_to_camel_case(self):
        self.assertEqual(to_camel_case("hello_world"), "helloWorld")
        self.assertEqual(to_camel_case("test_case"), "testCase")

    def test_convert_dict_keys_to_camel_case(self):
        test_dict = {"hello_world": {"nested_key": "value"}}
        expected = {"helloWorld": {"nestedKey": "value"}}
        self.assertEqual(convert_dict_keys_to_camel_case(test_dict), expected)

    def test_get_admin_status(self):
        admin_user = Mock()
        admin_user.is_admin = True
        self.assertTrue(get_admin_status(admin_user))
        self.assertFalse(get_admin_status(None))

    @patch.dict(os.environ, {'TEST_INT': '123'})
    def test_get_env_int(self):
        self.assertEqual(get_env_int('TEST_INT'), 123)
        self.assertEqual(get_env_int('MISSING', 456), 456)

    def test_sanitize_metric_name(self):
        self.assertEqual(sanitize_metric_name("test.metric"), "test_metric")
        self.assertEqual(sanitize_metric_name("test/metric"), "test_metric")

    def test_sanitize_header_name(self):
        self.assertEqual(sanitize_header_name("content-type"), "Content-Type")
        self.assertEqual(sanitize_header_name("x-custom-header"), "X-Custom-Header")

    def test_is_http_status_code(self):
        self.assertTrue(is_http_status_code("200"))
        self.assertTrue(is_http_status_code("20*"))
        self.assertFalse(is_http_status_code("600"))
        self.assertFalse(is_http_status_code("abc"))
