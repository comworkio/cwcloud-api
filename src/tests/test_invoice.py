from unittest import TestCase

from utils.invoice import increase_invoice_number

class TestInvoice(TestCase):
    def test_increase_invoice_number_nominal(self):
        # Given
        current_year = 2023
        max_invoice_ref = 1

        # When
        new_ref = increase_invoice_number(current_year, max_invoice_ref)

        # Then
        self.assertIsNotNone(new_ref)
        self.assertEqual(new_ref, "202300002")

    def test_increase_invoice_number_none(self):
        # Given
        current_year = 2023
        max_invoice_ref = None

        # When
        new_ref = increase_invoice_number(current_year, max_invoice_ref)

        # Then
        self.assertIsNotNone(new_ref)
        self.assertEqual(new_ref, "202300001")

    def test_increase_invoice_number_big_number(self):
        # Given
        current_year = 2023
        max_invoice_ref = 20003

        # When
        new_ref = increase_invoice_number(current_year, max_invoice_ref)

        # Then
        self.assertIsNotNone(new_ref)
        self.assertEqual(new_ref, "202320004")
