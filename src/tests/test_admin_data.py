from unittest import TestCase
from unittest.mock import Mock, patch

test_current_user = Mock()
mock_db = Mock()

class TestAdminData(TestCase):
    @patch('controllers.admin.iot.admin_data.get_datas', side_effect=lambda x, y: [{'id': '1', 'device_id': 'test'}])
    @patch('entities.iot.Data.Data')
    def test_get_datas(self, mock_data, get_datas):
        # Given
        from controllers.admin.iot.admin_data import get_datas
        
        # When
        result = get_datas(test_current_user, mock_db)

        # Then
        self.assertEqual(result[0]['id'], '1')
        self.assertEqual(result[0]['device_id'], 'test')

    @patch('controllers.admin.iot.admin_data.get_numeric_data', side_effect=lambda x, y: [{'id': '1', 'data_id': 'test', 'device_id': 'test', 'key': 'test', 'value': 1.0}])
    @patch('entities.iot.Data.NumericData')
    def test_get_numeric_data(self, mock_numeric_data, get_numeric_data):
        # Given
        from controllers.admin.iot.admin_data import get_numeric_data
        
        # When
        result = get_numeric_data(test_current_user, mock_db)

        # Then
        self.assertEqual(result[0]['id'], '1')
        self.assertEqual(result[0]['data_id'], 'test')
        self.assertEqual(result[0]['device_id'], 'test')
        self.assertEqual(result[0]['key'], 'test')
        self.assertEqual(result[0]['value'], 1.0)

    @patch('controllers.admin.iot.admin_data.get_string_data', side_effect=lambda x, y: [{'id': '1', 'data_id': 'test', 'device_id': 'test', 'key': 'test', 'value': 'test'}])
    @patch('entities.iot.Data.StringData')
    def test_get_string_data(self, mock_string_data, get_string_data):
        # Given
        from controllers.admin.iot.admin_data import get_string_data
        
        # When
        result = get_string_data(test_current_user, mock_db)

        # Then
        self.assertEqual(result[0]['id'], '1')
        self.assertEqual(result[0]['data_id'], 'test')
        self.assertEqual(result[0]['device_id'], 'test')
        self.assertEqual(result[0]['key'], 'test')
        self.assertEqual(result[0]['value'], 'test')
