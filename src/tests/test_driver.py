from unittest import TestCase
from unittest.mock import patch

from utils.driver import sanitize_project_name

class TestDomain(TestCase):
    @patch('utils.driver.is_true', return_value = True)
    def test_sanitize_project_name_enable(self, mock_is_true):
        # Given
        user_email = "name.surname@usermail.com"

        # When
        sanitized_name = sanitize_project_name(user_email)

        # Then
        self.assertEqual(sanitized_name, 'name.surname_usermail.com')

    @patch('utils.driver.is_true', return_value = False)
    def test_sanitize_project_name_disable(self, mock_is_true):
        # Given
        user_email = "name.surname@usermail.com"

        # When
        sanitized_name = sanitize_project_name(user_email)

        # Then
        self.assertEqual(sanitized_name, 'name.surname@usermail.com')
