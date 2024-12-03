from unittest import TestCase

from utils.observability.monitor import check_status_code_pattern

class TestMonitor(TestCase):
    def test_check_status_code_pattern_200(self):
        # Given
        actual_code = 200
        pattern = '20*'

        # When
        result = check_status_code_pattern(actual_code, pattern)

        # Then
        self.assertTrue(result)

    def test_check_status_code_pattern_201(self):
        # Given
        actual_code = 201
        pattern = '20*'

        # When
        result = check_status_code_pattern(actual_code, pattern)

        # Then
        self.assertTrue(result)

    def test_check_status_code_pattern_400_ko(self):
        # Given
        actual_code = 400
        pattern = '20*'

        # When
        result = check_status_code_pattern(actual_code, pattern)

        # Then
        self.assertFalse(result)
