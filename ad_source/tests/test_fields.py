from unittest import TestCase

from ad_source.fields import MoneyField


class FieldTestCase(TestCase):
    def setUp(self) -> None:
        self.field = MoneyField

    def test_deconstruct(self):
        field_instance = MoneyField(max_digits=14, decimal_places=2, default_currency='ETH')
        name, path, args, kwargs = field_instance.deconstruct()
        new_instance = MoneyField(*args, **kwargs)
        self.assertEqual(field_instance.max_digits, new_instance.max_digits)
        self.assertEqual(field_instance.decimal_places, new_instance.decimal_places)
        self.assertEqual(field_instance.default_currency, new_instance.default_currency)
