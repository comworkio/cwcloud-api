from unittest import TestCase
from unittest.mock import Mock, patch

test_current_user = Mock()
mock_db = Mock()
mock_bt = Mock()

class TestTrigger(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestTrigger, self).__init__(*args, **kwargs)
    
    @patch.dict('os.environ', {'TRIGGERS_CHANNEL': 'mock_triggers_channel', 'TRIGGERS_GROUP': 'mock_triggers_group'})
    @patch('controllers.faas.triggers.add_trigger', side_effect=lambda x,y,z: {'code': 201, 'id': 1, 'created_at': '2020-01-01', 'updated_at': '2020-01-01'})
    @patch('utils.faas.triggers.is_not_supported_kind', side_effect=lambda x: x)
    @patch('utils.faas.owner.get_owner_id', side_effect=lambda x,y: x)
    def test_add_trigger(self, add_trigger, is_not_supported_kind, get_owner_id):
        # Given
        from entities.faas.Trigger import TriggerEntity
        from controllers.faas.triggers import add_trigger
        
        trigger = TriggerEntity()
        trigger.id = 1
        trigger.is_public = True
        trigger.content = {}
        trigger.owner_id = 1
        trigger.created_at = '2020-01-01'
        trigger.updated_at = '2020-01-01'
        
        # When
        result = add_trigger(trigger, test_current_user, mock_db)
        
        # Then
        self.assertEqual(result['code'], 201)
        self.assertIsNotNone(result['id'])
        self.assertIsNotNone(result['created_at'])
        self.assertIsNotNone(result['updated_at'])
    
    @patch.dict('os.environ', {'TRIGGERS_CHANNEL': 'mock_triggers_channel', 'TRIGGERS_GROUP': 'mock_triggers_group'})
    @patch('controllers.faas.triggers.override_trigger', side_effect=lambda id, current_user, trigger, db: {'status': 'ok', 'code': 200, 'id': '', 'updated_at': '2020-01-01'})
    @patch('utils.faas.triggers.is_not_supported_kind', side_effect=lambda x: x)   
    @patch('utils.common.is_true', side_effect=lambda x: x)  
    @patch('utils.faas.owner.override_owner_id', side_effect= lambda x, y, z: x)
    def test_override_trigger(self, override_trigger, is_not_supported_kind, is_true, override_owner_id):
        # Given
        from entities.faas.Trigger import TriggerEntity
        from controllers.faas.triggers import override_trigger
        
        trigger = TriggerEntity()
        trigger.id = 1
        trigger.is_public = True
        trigger.content = {}
        trigger.owner_id = 1
        trigger.created_at = '2020-01-01'
        trigger.updated_at = '2020-01-01'
        
        # When
        result = override_trigger(1, test_current_user, trigger, mock_db)
        
        # Then
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['code'], 200)
        self.assertEqual(result['id'], '')
        self.assertIsNotNone(result['updated_at'])

    @patch.dict('os.environ', {'TRIGGERS_CHANNEL': 'mock_triggers_channel', 'TRIGGERS_GROUP': 'mock_triggers_group'})
    @patch('utils.common.is_true', side_effect=lambda x: x) 
    @patch('controllers.faas.triggers.get_trigger', side_effect=lambda x, y, z: {'status': 'ok', 'code':  200})    
    def test_get_trigger(self, get_trigger, is_true):
        # Given
        from entities.faas.Trigger import TriggerEntity
        from controllers.faas.triggers import get_trigger
        
        trigger = TriggerEntity()
        trigger.id = 1
        trigger.is_public = True
        trigger.content = {}
        trigger.owner_id = 1
        trigger.created_at = '2020-01-01'
        trigger.updated_at = '2020-01-01'
        
        # When
        result = get_trigger(1, test_current_user, mock_db)
        
        # Then
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['code'], 200)

    @patch.dict('os.environ', {'TRIGGERS_CHANNEL': 'mock_triggers_channel', 'TRIGGERS_GROUP': 'mock_triggers_group'})
    @patch('utils.common.is_true', side_effect=lambda x: x) 
    @patch('controllers.faas.triggers.delete_trigger', side_effect=lambda x, y, z: {'status': 'ok', 'code': 200})
    def test_delete_trigger(self, is_true, delete_trigger):
        # Given
        from controllers.faas.triggers import delete_trigger
        
        # When
        result = delete_trigger(1, test_current_user, mock_db)
        
        # Then
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['code'], 200)
     
    @patch.dict('os.environ', {'TRIGGERS_CHANNEL': 'mock_triggers_channel', 'TRIGGERS_GROUP': 'mock_triggers_group'})
    @patch('controllers.faas.triggers.get_my_triggers', side_effect=lambda db, current_user, kind, start_index, max_results: {'status': 'ok','code': 200,'kind': 'kind','start_index': start_index, 
    'max_results': max_results, 'results': [{"id": 1,"is_public": True,"content": {},"created_at": '2020-01-01',"updated_at": '2020-01-01', "owner": {"id": 1,"username": "test_user"}}]})
    @patch('utils.common.is_not_numeric', side_effect=lambda x: x)    
    @patch('utils.common.is_not_empty', side_effect=lambda x: x)
    def test_get_my_triggers(self, get_my_triggers, is_not_numeric, is_not_empty):
        # Given
        from controllers.faas.triggers import get_my_triggers
        from entities.faas.Trigger import TriggerEntity
        
        trigger = TriggerEntity()
        trigger.id = 1
        trigger.is_public = True
        trigger.content = {}
        trigger.owner_id = 1
        trigger.created_at = '2020-01-01'
        trigger.updated_at = '2020-01-01'
        
        # When
        result = get_my_triggers(mock_db, test_current_user, kind='kind', start_index='start_index', max_results='max_results')
        
        # Then
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['code'], 200)
        self.assertEqual(result['start_index'], 'start_index')
        self.assertEqual(result['max_results'], 'max_results')
        self.assertIsNotNone(result['results'])

    @patch.dict('os.environ', {'TRIGGERS_CHANNEL': 'mock_triggers_channel', 'TRIGGERS_GROUP': 'mock_triggers_group'})
    @patch('controllers.faas.triggers.get_all_triggers', side_effect=lambda db, current_user, kind, start_index, max_results: {'status': 'ok', 'code': 200, 'start_index': start_index, 
    'max_results': max_results,'results': [{"id": 1, "kind": "kind", "content": {}, "created_at": '2020-01-01', "updated_at": '2020-01-01', "owner": {"id": 1, "username": "test_user"}}]})
    @patch('utils.common.is_not_numeric', side_effect=lambda x: x)
    @patch('utils.common.is_not_empty', side_effect=lambda x: x)
    @patch('utils.common.is_false', side_effect=lambda x: x)    
    def test_get_all_triggers(self, get_all_triggers, is_not_numeric, is_not_empty, is_false):
        # Given
        from controllers.faas.triggers import get_all_triggers
        
        # When
        result = get_all_triggers(mock_db, test_current_user, kind='kind', start_index='start_index', max_results='max_results')
        
        # Then
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['code'], 200)
        self.assertEqual(result['start_index'], 'start_index')
        self.assertEqual(result['max_results'], 'max_results')
        self.assertEqual(result['results'], [
            {
                "id": 1,
                "kind": "kind",
                "content": {},
                "created_at": '2020-01-01',
                "updated_at": '2020-01-01',
                "owner": {
                    "id": 1,
                    "username": "test_user"
                }
            }
        ])
