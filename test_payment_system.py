import unittest
from datetime import date, timedelta

from payment_validator import PaymentValidator, ValidationResult
from refund_processor import RefundProcessor, RefundResult
from tax_calculator import TaxCalculator


class TestTaxCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = TaxCalculator()

    def test_igv_standard_rate(self):
        self.assertAlmostEqual(self.calc.calculate_tax(100.0, 0.18), 18.0)

    def test_zero_rate(self):
        self.assertAlmostEqual(self.calc.calculate_tax(200.0, 0.0), 0.0)

    def test_negative_amount_raises(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(-50.0, 0.18)

    def test_total_with_tax(self):
        self.assertAlmostEqual(self.calc.total_with_tax(100.0, 0.18), 118.0)

    def test_named_igv_rate(self):
        self.assertAlmostEqual(
            self.calc.calculate_tax_by_name(100.0, "IGV"), 18.0
        )

    def test_invalid_rate_raises(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_tax(100.0, 1.5)

    def test_unknown_named_rate_raises(self):
        with self.assertRaises(KeyError):
            self.calc.calculate_tax_by_name(100.0, "NO_EXISTE")


class TestPaymentValidator(unittest.TestCase):
    def setUp(self):
        self.validator = PaymentValidator(min_amount=1.0, daily_limit=1000.0)

    def test_amount_below_minimum_rejected(self):
        result = self.validator.validate(amount=0.5, spent_today=0.0)
        self.assertFalse(result.approved)
        self.assertIn("mínimo", result.reason.lower())

    def test_amount_above_daily_limit_rejected(self):
        result = self.validator.validate(amount=200.0, spent_today=900.0)
        self.assertFalse(result.approved)
        self.assertIn("diario", result.reason.lower())

    def test_valid_payment_approved(self):
        result = self.validator.validate(amount=50.0, spent_today=100.0)
        self.assertTrue(result.approved)

    def test_exact_daily_limit_approved(self):
        result = self.validator.validate(amount=900.0, spent_today=100.0)
        self.assertTrue(result.approved)

    def test_zero_amount_rejected(self):
        result = self.validator.validate(amount=0.0, spent_today=0.0)
        self.assertFalse(result.approved)


class TestRefundProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = RefundProcessor(max_days=30)
        self.purchase_date = date.today() - timedelta(days=10)

    def test_full_refund_within_policy(self):
        result = self.processor.process(
            original_amount=150.0,
            refund_amount=150.0,
            purchase_date=self.purchase_date,
        )
        self.assertTrue(result.approved)
        self.assertAlmostEqual(result.refund_amount, 150.0)

    def test_partial_refund_within_policy(self):
        result = self.processor.process(
            original_amount=150.0,
            refund_amount=75.0,
            purchase_date=self.purchase_date,
        )
        self.assertTrue(result.approved)
        self.assertAlmostEqual(result.refund_amount, 75.0)

    def test_refund_exceeds_original_rejected(self):
        result = self.processor.process(
            original_amount=100.0,
            refund_amount=120.0,
            purchase_date=self.purchase_date,
        )
        self.assertFalse(result.approved)
        self.assertIn("original", result.reason.lower())

    def test_refund_outside_policy_window_rejected(self):
        old_purchase = date.today() - timedelta(days=45)
        result = self.processor.process(
            original_amount=100.0,
            refund_amount=100.0,
            purchase_date=old_purchase,
        )
        self.assertFalse(result.approved)
        self.assertIn("plazo", result.reason.lower())

    def test_negative_refund_raises(self):
        with self.assertRaises(ValueError):
            self.processor.process(
                original_amount=100.0,
                refund_amount=-10.0,
                purchase_date=self.purchase_date,
            )


if __name__ == '__main__':
    unittest.main(verbosity=2)
