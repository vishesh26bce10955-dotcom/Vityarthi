import json
import os
import tempfile
import unittest
from decimal import Decimal

from tracker.Expense_Manager import ExpenseManager
from tracker.Storage import JsonStorage


class TestExpenseManager(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.fileName = os.path.join(self.folder.name, "expenses.json")
        self.manager = ExpenseManager(JsonStorage(self.fileName))

    def tearDown(self):
        self.folder.cleanup()

    def addSample(self):
        self.manager.addExpense("100", "food", "Groceries", "2026-08-01")
        self.manager.addExpense("250.50", "travel", "Train ticket", "2026-08-05")
        self.manager.addExpense("40", "food", "Snacks", "2026-09-02")

    def testAddAssignsIncreasingIds(self):
        self.assertEqual(self.manager.addExpense("10", "food", "Tea", "2026-08-01"), "Expense added with ID 1.")
        self.assertEqual(self.manager.addExpense("20", "food", "Tea", "2026-08-01"), "Expense added with ID 2.")

    def testAddRejectsInvalidInput(self):
        with self.assertRaises(ValueError):
            self.manager.addExpense("-5", "food", "Tea", "2026-08-01")
        self.assertEqual(self.manager.listExpenses(), [])

    def testDataPersistsAcrossRestart(self):
        self.addSample()
        reloaded = ExpenseManager(JsonStorage(self.fileName))
        self.assertEqual(len(reloaded.listExpenses()), 3)
        self.assertEqual(reloaded.addExpense("5", "food", "Gum", "2026-09-03"), "Expense added with ID 4.")

    def testUpdateOnlyChangesGivenFields(self):
        self.addSample()
        self.manager.updateExpense(1, amount="120")
        expense = self.manager.getExpense(1)
        self.assertEqual(expense.amount, Decimal("120.00"))
        self.assertEqual(expense.category, "Food")

    def testUpdateWithInvalidValueChangesNothing(self):
        self.addSample()
        with self.assertRaises(ValueError):
            self.manager.updateExpense(1, amount="120", date="bad")
        self.assertEqual(self.manager.getExpense(1).amount, Decimal("100.00"))

    def testDelete(self):
        self.addSample()
        self.manager.deleteExpense(2)
        self.assertEqual([expense.expenseId for expense in self.manager.listExpenses()], [1, 3])
        with self.assertRaises(ValueError):
            self.manager.deleteExpense(2)

    def testSearchFilters(self):
        self.addSample()
        self.assertEqual(len(self.manager.searchExpenses(category="food")), 2)
        self.assertEqual(len(self.manager.searchExpenses(keyword="TRAIN")), 1)
        self.assertEqual(len(self.manager.searchExpenses(startDate="2026-09-01")), 1)
        self.assertEqual(len(self.manager.searchExpenses(minAmount="50", maxAmount="200")), 1)

    def testCorruptFileIsBackedUp(self):
        with open(self.fileName, "w") as newFile:
            newFile.write("{not json")
        manager = ExpenseManager(JsonStorage(self.fileName))
        self.assertEqual(manager.listExpenses(), [])
        self.assertTrue(any(".corrupt-" in name for name in os.listdir(self.folder.name)))

    def testSaveIsValidJson(self):
        self.addSample()
        with open(self.fileName, "r") as newFile:
            self.assertEqual(len(json.load(newFile)["expenses"]), 3)


if __name__ == "__main__":
    unittest.main()
