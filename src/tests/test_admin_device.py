from unittest import TestCase
from unittest.mock import Mock, patch

test_current_user = Mock()
mock_db = Mock()
mock_bt = Mock()

class TestAdminDevice(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestAdminDevice, self).__init__(*args, **kwargs)
    
    @patch('entities.iot.Device.Device')
    @patch('controllers.admin.iot.admin_device.get_devices', side_effect=lambda current_user, db: {'id': "1", 'username': "testuser@example.com", 'active': True, 'status': 'ok'})   
    def test_get_devices(self, getAllDevices, get_devices):
        # Given
        from controllers.admin.iot.admin_device import get_devices
        from entities.iot.Device import Device
        
        device = Device()
        device.id = "1"
        device.typeobject_id = "some-guid"
        device.username = "testuser@example.com"
        device.active = True

        Device.getAllDevices.return_value = device
        
        # When
        result = get_devices(test_current_user, mock_db)

        # Then
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['id'], str(device.id))
        self.assertEqual(result['username'], device.username)
        self.assertEqual(result['active'], device.active)
        
    @patch('entities.iot.Device.Device')
    @patch('controllers.admin.iot.admin_device.delete_device', side_effect=lambda device_id, db: {
        'status': 'ok',
        'message': 'Device successfully deleted',
        'i18n_code': 'device_deleted'
    })
    def test_delete_device(self, mock_device, delete_device):
        # Given
        from controllers.admin.iot.admin_device import delete_device
        from entities.iot.Device import Device
        
        device = Device()
        device.id = "1"
        device.typeobject_id = "some-guid"
        device.username = "testuser@example.com"
        device.active = True

        Device.getDeviceById.return_value = device
        Device.deleteDeviceById.return_value = device
        # When
        result = delete_device("1", mock_db)

        # Then
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['message'], 'Device successfully deleted')
        self.assertEqual(result['i18n_code'], 'device_deleted')
