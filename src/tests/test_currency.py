from unittest import TestCase

from utils.currency import get_payment_currency_from_unit

class TestCurrency(TestCase):
    def test_dollars_1(self):
        # Given
        price_unit = "$"

        # When
        currency = get_payment_currency_from_unit(price_unit)

        # Then
        self.assertEqual(currency, "usd")

    def test_dollars_2(self):
        # Given
        price_unit = "dollars"

        # When
        currency = get_payment_currency_from_unit(price_unit)

        # Then
        self.assertEqual(currency, "usd")

    def test_tnd_1(self):
        # Given
        price_unit = "dt"

        # When
        currency = get_payment_currency_from_unit(price_unit)

        # Then
        self.assertEqual(currency, "tnd")

    def test_tnd_2(self):
        # Given
        price_unit = "dinars"

        # When
        currency = get_payment_currency_from_unit(price_unit)

        # Then
        self.assertEqual(currency, "tnd")

    def test_euros_1(self):
        # Given
        price_unit = "euros"

        # When
        currency = get_payment_currency_from_unit(price_unit)

        # Then
        self.assertEqual(currency, "eur")

    def test_euros_2(self):
        # Given
        price_unit = "€"

        # When
        currency = get_payment_currency_from_unit(price_unit)

        # Then
        self.assertEqual(currency, "eur")
