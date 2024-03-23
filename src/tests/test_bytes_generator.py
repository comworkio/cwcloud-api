from unittest import TestCase
from unittest.mock import Mock, patch
from utils.bytes_generator import generate_hashed_name

class TestGenerateHashedName(TestCase):
    @patch('utils.bytes_generator.is_true', return_value=True)
    def test_generate_hashed_name_enable(self, mock_is_true):
        # Test when _disable_dynamic_names is True
        _, name = generate_hashed_name('test')
        self.assertEqual(name, 'test')

    @patch('utils.bytes_generator.is_true', return_value=False)
    def test_generate_hashed_name_disable(self, mock_is_true):
        # Test when _disable_dynamic_names is False
        hash, hashed_name = generate_hashed_name('test')
        self.assertEqual(len(hash), 6)
        self.assertTrue(hashed_name.startswith('test-'))
