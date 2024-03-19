from unittest import TestCase
from unittest.mock import Mock, patch

test_current_user = Mock()
mock_db = Mock()
mock_bt = Mock()

class TestTemplate(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestTemplate, self).__init__(*args, **kwargs)
    
    @patch('controllers.faas.templates.generate_template', side_effect=lambda x: {'code': 200, 'languages': ['go', 'java', 'javascript', 'python'], 'status': 'ok'})    
    @patch('utils.faas.functions.is_not_supported_language', side_effect=lambda x: x)
    def  test_generate_template(self, generate_template, is_not_supported_language):
        # Given
        from controllers.faas.templates import generate_template
        
        # When
        result = generate_template(test_current_user)
        
        # Then
        self.assertEqual(result['code'], 200)
        self.assertEqual(result['status'], 'ok')
