from unittest import TestCase
from unittest.mock import Mock, patch

test_current_user = Mock()
mock_db = Mock()
mock_bt = Mock()

class TestObjectType(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestObjectType, self).__init__(*args, **kwargs)
        
    @patch('controllers.iot.object_type.get_object_types', return_value={'id': '1', 'user_id': '1', 'content': 'test'})
    @patch('entities.iot.ObjectType.ObjectType.getUserObjectTypes')
    def test_get_object_types(self, getUserObjectTypes, get_object_types):
        # Given
        from controllers.iot.object_type import get_object_types
        from entities.iot.ObjectType import ObjectType
        
        objecttype = ObjectType()
        objecttype.id = "1"
        objecttype.user_id = "1"
        objecttype.content = "test"
        
        ObjectType.getUserObjectTypes.return_value = objecttype
        
        # When 
        result = get_object_types(test_current_user, mock_db)
        
        # Then 
        self.assertEqual(result['id'], '1')
        self.assertEqual(result['user_id'], '1')
        self.assertEqual(result['content'], 'test')
        
    @patch('controllers.iot.object_type.get_object_type', return_value={'id': '1', 'user_id': '1', 'content': 'test'})
    @patch('entities.iot.ObjectType.ObjectType.findUserObjectTypeById')
    def test_get_object_type(self, findUserObjectTypeById, get_object_type ):
        # Given
        from controllers.iot.object_type import get_object_type
        from entities.iot.ObjectType import ObjectType
        
        objecttype = ObjectType()
        objecttype.id = "1"
        objecttype.user_id = "1"
        objecttype.content = "test"
        
        ObjectType.findUserObjectTypeById.return_value = objecttype
       
        # When
        result = get_object_type(test_current_user, "1", mock_db)
        
        # Then
        self.assertEqual(result['id'], '1')
        self.assertEqual(result['user_id'], '1')
        self.assertEqual(result['content'], 'test') 
    
    @patch('controllers.iot.object_type.add_object_type',side_effect=lambda x, y, z: {
        'status': 'ok',
        'message': 'Object type successfully created',
    })    
    def test_add_object_type(self, add_object_type):
        # Given
        from controllers.iot.object_type import add_object_type
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
        
    @patch('controllers.iot.object_type.update_object_type',side_effect=lambda x, y, z,w: {
        'status': 'ok',
        'message': 'Object type successfully updated',
    })    
    @patch('entities.iot.ObjectType.ObjectType.findUserObjectTypeById')
    def test_update_object_type(self, update_object_type,findUserObjectTypeById):
        # Given
        from controllers.iot.object_type import update_object_type
        from entities.iot.ObjectType import ObjectType
        from schemas.iot.ObjectType import ObjectTypeSchema, ObjectTypeContent

        payload = ObjectTypeSchema(
        content=ObjectTypeContent(
            public=True,  # Add required fields
            name="exampleName",
            decoding_function="exampleFunction",
            triggers=["trigger1", "trigger2"]
        ))
        
        objecttype = ObjectType()
        objecttype.id = "1"
        objecttype.user_id = "1"
        objecttype.content = "test"
        
        ObjectType.findUserObjectTypeById.return_value = objecttype
        
        # When
        result = update_object_type(test_current_user, "1", payload, mock_db)
        
        # Then
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['message'], 'Object type successfully updated')
