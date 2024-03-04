from unittest import TestCase
from unittest.mock import Mock, patch
from fastapi.responses import JSONResponse

test_current_user = Mock()
mock_db = Mock()
mock_bt = Mock()

class Testget_all_triggers_kinds(TestCase):
    def __init__(self, *args, **kwargs):
        super(Testget_all_triggers_kinds, self).__init__(*args, **kwargs)
    
    @patch('controllers.faas.trigger_kinds.get_all_triggers_kinds', return_value={'status': 'ok', 'code': 200, 'kinds': ['cron']})
    def test_get_all_triggers_kinds(self, get_all_triggers_kinds):
        # Given
        from controllers.faas.trigger_kinds import get_all_triggers_kinds
        
        # When
        result = get_all_triggers_kinds()
        
        # Then
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['code'], 200)
        self.assertEqual(result['kinds'], ['cron'])
