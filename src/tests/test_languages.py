from unittest import TestCase
from unittest.mock import Mock, patch
from fastapi.responses import JSONResponse
from schemas.User import UserSchema
from controllers.faas.languages import _supported_languages

test_current_user = Mock()
mock_db = Mock()
mock_bt = Mock()

class TestLanguages(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestLanguages, self).__init__(*args, **kwargs)

    @patch('controllers.faas.languages.get_supported_languages', side_effect=lambda x: {'status': 'ok', 'code': 200, 'languages': _supported_languages})
    def test_get_supported_languages(self, get_supported_languages):
        # Given
        from controllers.faas.languages import get_supported_languages, _supported_languages
    
        # When
        result = get_supported_languages(test_current_user)

        # Then
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['code'], 200)
        self.assertEqual(result['languages'],  _supported_languages)
