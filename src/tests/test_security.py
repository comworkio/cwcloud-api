from unittest import TestCase
from utils.security import check_password, is_not_email_valid, random_password

class TestSecurity(TestCase):
    def test_check_password_nominal(self):
        # Given
        password = "pasSword123$"

        # When
        check = check_password(password)

        # Then
        self.assertEqual(check['status'], True)

    def test_check_password_missing_capital(self):
        # Given
        password = "password123$"

        # When
        check = check_password(password)

        # Then
        self.assertEqual(check['status'], False)
        self.assertEqual(check['i18n_code'], 'password_no_upper')

    def test_check_password_missing_lower(self):
        # Given
        password = "PASSWORD$"

        # When
        check = check_password(password)

        # Then
        self.assertEqual(check['status'], False)
        self.assertEqual(check['i18n_code'], 'password_no_number')

    def test_check_password_no_special_char(self):
        # Given
        password = "pasSword123"

        # When
        check = check_password(password)

        # Then
        self.assertEqual(check['status'], False)
        self.assertEqual(check['i18n_code'], 'password_no_symbol')

    def test_check_password_too_short(self):
        # Given
        password = "pasS1$"

        # When
        check = check_password(password)

        # Then
        self.assertEqual(check['status'], False)
        self.assertEqual(check['i18n_code'], 'password_too_short')

    def test_is_not_email_valid(self):
        # Given
        email = "toto.titi@gmail.com"

        # When
        check = is_not_email_valid(email)

        # Then
        self.assertEqual(check, False)

    def test_is_not_email_valid_invalid(self):
        # Given
        email = "toto.titi@"

        # When
        check = is_not_email_valid(email)

        # Then
        self.assertEqual(check, True)

    def test_random_password(self):
        # When
        check = check_password(random_password(10))

        # Then
        self.assertEqual(check['status'], True)
