from unittest import TestCase
from unittest.mock import patch

from utils.dynamic_name import generate_hashed_name, rehash_dynamic_name

class TestDynamicName(TestCase):
    @patch('utils.dynamic_name.is_true', return_value = True)
    def test_generate_hashed_name_enable(self, mock_is_true):
        hash, name = generate_hashed_name('test')
        self.assertEqual(len(hash), 0)
        self.assertEqual(name, 'test')

    @patch('utils.dynamic_name.is_true', return_value = False)
    def test_generate_hashed_name_disable(self, mock_is_true):
        hash, hashed_name = generate_hashed_name('test')
        self.assertEqual(len(hash), 6)
        self.assertTrue(hashed_name.startswith('test-'))

    @patch('utils.dynamic_name.is_true', return_value = True)
    def test_rehash_dynamic_name_enable(self, mock_is_true):
        result = rehash_dynamic_name('test', 'suffix')
        self.assertEqual(result, 'test')

    @patch('utils.dynamic_name.is_true', return_value = False)
    def test_rehash_dynamic_name_disable(self, mock_is_true):
        result = rehash_dynamic_name('test', 'suffix')
        self.assertEqual(result, 'test-suffix')

    @patch('utils.dynamic_name.is_true', return_value = False)
    def test_rehash_dynamic_name_empty(self, mock_is_true):
        result = rehash_dynamic_name('test', '')
        self.assertEqual(result, 'test')
