from unittest import TestCase
from unittest.mock import patch, Mock
from entities.iot.ObjectType import ObjectType

test_current_user = Mock()
mock_db = Mock()
mock_bt = Mock()

class TestAdminObjectType(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestAdminObjectType, self).__init__(*args, **kwargs)
        
    @patch('controllers.admin.iot.admin_object_type.get_object_types')
    def test_admin_get_object_types(self, mock_get_object_types):
        # Given
        from controllers.admin.iot.admin_object_type import get_object_types
        mock_get_object_types.return_value = [ObjectType(id='1', user_id='1', content='test')]
        
        # When  
        result = get_object_types(test_current_user, mock_db)
        
        # Then
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], ObjectType)
        self.assertEqual(result[0].id, '1')
        self.assertEqual(result[0].user_id, '1')
        self.assertEqual(result[0].content, 'test')

    @patch('controllers.admin.iot.admin_object_type.get_object_type')
    def test_admin_get_object_type(self, mock_get_object_type):
        # Given
        from controllers.admin.iot.admin_object_type import get_object_type
        mock_get_object_type.return_value = ObjectType(id='1', user_id='1', content='test')
                
        # When
        result = get_object_type(test_current_user, '1', mock_db)
        
        # Then
        self.assertIsInstance(result, ObjectType)
        self.assertEqual(result.id, '1')
        self.assertEqual(result.user_id, '1')
        self.assertEqual(result.content, 'test')

    @patch('controllers.admin.iot.admin_object_type.update_object_type', side_effect = lambda current_user, object_type_id, payload, db: {
            'status': 'ok',
            'message': 'Object type successfully updated',
        })
    def test_admin_update_object_type(self, mock_update_object_type):
        # Given
        from controllers.admin.iot.admin_object_type import update_object_type
        from schemas.iot.ObjectType import ObjectTypeSchema, ObjectTypeContent

        payload = ObjectTypeSchema(
        content=ObjectTypeContent(
            public=True,  # Add required fields
            name="exampleName",
            decoding_function="exampleFunction",
            triggers=["trigger1", "trigger2"]
        ))
    
        # When
        result = update_object_type(test_current_user, '1', payload, mock_db)
        
        # Then
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['message'], 'Object type successfully updated')

    @patch('controllers.admin.iot.admin_object_type.add_object_type', side_effect = lambda current_user, payload, db: {
            'status': 'ok',
            'message': 'Object type successfully created',
        })
    def test_admin_add_object_type(self, mock_add_object_type):
        # Given
        from controllers.admin.iot.admin_object_type import add_object_type
        from schemas.iot.ObjectType import ObjectTypeSchema, ObjectTypeContent

        payload = ObjectTypeSchema(
        content=ObjectTypeContent(
            public=True,  # Add required fields
            name="exampleName",
            decoding_function="exampleFunction",
            triggers=["trigger1", "trigger2"]
        ))
        
        # When
        result = add_object_type(test_current_user, payload, mock_db)
        
        # Then
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['message'], 'Object type successfully created')

    @patch('controllers.admin.iot.admin_object_type.delete_object_type', side_effect = lambda current_user, object_type_id, db: {
            'status': 'ok',
            'message': 'Object type successfully deleted',
        })
    def test_admin_delete_object_type(self, mock_delete_object_type):
        # Given
        from controllers.admin.iot.admin_object_type import delete_object_type

        object_type_id = 1
        
        # When
        result = delete_object_type(test_current_user, object_type_id, mock_db)
        
        # Then
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['message'], 'Object type successfully deleted')
