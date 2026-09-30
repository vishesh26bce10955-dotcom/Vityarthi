import unittest
from datetime import date, timedelta
from decimal import Decimal

from tracker.Validators import (validateAmount, validateCategory, validateDate, validateDescription,
                                validateId, validateMonth)


class TestValidators(unittest.TestCase):
    def testAmountIsRoundedToTwoPlaces(self):
        self.assertEqual(validateAmount(" 12.5 "), Decimal("12.50"))

    def testAmountRejectsBadValues(self):
        for text in ["abc", "0", "-5", "NaN", "Infinity", "99999999999", ""]:
            with self.assertRaises(ValueError):
                validateAmount(text)

    def testDateAcceptsIsoFormat(self):
        self.assertEqual(validateDate("2026-01-15"), "2026-01-15")

    def testDateRejectsBadAndFutureDates(self):
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        for text in ["15-01-2026", "2026-13-01", "hello", tomorrow]:
            with self.assertRaises(ValueError):
                validateDate(text)

    def testMonth(self):
        self.assertEqual(validateMonth("2026-3"), "2026-03")
        with self.assertRaises(ValueError):
            validateMonth("2026-13")
        with self.assertRaises(ValueError):
            validateMonth("March")

    def testCategoryIsCleaned(self):
        self.assertEqual(validateCategory("  eating   out "), "Eating Out")
        with self.assertRaises(ValueError):
            validateCategory("   ")

    def testDescription(self):
        self.assertEqual(validateDescription("  Lunch   with team "), "Lunch with team")
        with self.assertRaises(ValueError):
            validateDescription("x" * 100)

    def testId(self):
        self.assertEqual(validateId("7"), 7)
        for text in ["0", "-1", "x"]:
            with self.assertRaises(ValueError):
                validateId(text)


if __name__ == "__main__":
    unittest.main()
