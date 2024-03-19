from unittest import TestCase

from utils.domain import is_not_subdomain_valid

class TestDomain(TestCase):
    def test_is_not_subdomain_valid_valid(self):
        # Given
        subdomain = "test-prod9"

        # When
        check = is_not_subdomain_valid(subdomain)

        # Then
        self.assertEqual(check, False)

    def test_is_not_subdomain_valid_invalid(self):
        # Given
        subdomain = "test_prod9"

        # When
        check = is_not_subdomain_valid(subdomain)

        # Then
        self.assertEqual(check, True)
