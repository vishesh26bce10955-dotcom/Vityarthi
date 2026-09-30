import os
import tempfile
import unittest
from decimal import Decimal

from tracker.Budget_Manager import BudgetManager
from tracker.Csv_Transfer import exportCsv, importCsv, makeSafeCell, undoSafeCell
from tracker.Expense_Manager import ExpenseManager
from tracker.Reports import categoryChart, categoryTotals, monthlySummary, monthlyTrend, topExpenses, totalAmount
from tracker.Storage import JsonStorage


class TestBudgetAndReports(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        storage = JsonStorage(os.path.join(self.folder.name, "expenses.json"))
        self.expenses = ExpenseManager(storage)
        self.budgets = BudgetManager(storage, self.expenses)
        self.expenses.addExpense("900", "food", "Groceries", "2026-08-01")
        self.expenses.addExpense("300", "travel", "Train", "2026-08-05")
        self.expenses.addExpense("50", "food", "Snacks", "2026-09-02")

    def tearDown(self):
        self.folder.cleanup()

    def testBudgetStatusLabels(self):
        self.budgets.setBudget("food", "1000")
        self.budgets.setBudget("travel", "250")
        self.budgets.setBudget("fun", "500")
        labels = {row[0]: row[4] for row in self.budgets.budgetStatus("2026-08")}
        self.assertEqual(labels, {"Food": "WARNING", "Travel": "OVER BUDGET", "Fun": "OK"})

    def testBudgetAlertsOnlyForProblems(self):
        self.budgets.setBudget("food", "1000")
        self.budgets.setBudget("fun", "500")
        self.assertEqual(len(self.budgets.budgetAlerts("2026-08")), 1)
        self.assertEqual(self.budgets.budgetAlerts("2026-09"), [])

    def testRemoveMissingBudgetFails(self):
        with self.assertRaises(ValueError):
            self.budgets.removeBudget("food")

    def testTotalsAndCategories(self):
        allExpenses = self.expenses.listExpenses()
        self.assertEqual(totalAmount(allExpenses), Decimal("1250.00"))
        self.assertEqual(list(categoryTotals(allExpenses).items())[0], ("Food", Decimal("950.00")))

    def testMonthlySummary(self):
        summary = monthlySummary(self.expenses.listExpenses(), "2026-08")
        self.assertIn("Total spent: 1200.00", summary)
        self.assertEqual(monthlySummary([], "2026-08"), "No expenses found for 2026-08.")

    def testTopExpenses(self):
        top = topExpenses(self.expenses.listExpenses(), 2)
        self.assertEqual([expense.expenseId for expense in top], [1, 2])
        with self.assertRaises(ValueError):
            topExpenses([], 0)

    def testChartsHandleEmptyData(self):
        self.assertEqual(categoryChart([]), "No expenses to chart.")
        self.assertIn("2026-09", monthlyTrend(self.expenses.listExpenses()))

    def testCsvRoundTripAndFormulaGuard(self):
        self.expenses.addExpense("10", "misc", "=SUM(A1)", "2026-09-03")
        path = os.path.join(self.folder.name, "out.csv")
        exportCsv(self.expenses.listExpenses(), path)
        with open(path, "r") as newFile:
            self.assertIn("'=SUM(A1)", newFile.read())
        fresh = ExpenseManager(JsonStorage(os.path.join(self.folder.name, "fresh.json")))
        self.assertEqual(importCsv(fresh, path), "Imported 4 expenses from " + path + ".")
        self.assertEqual(fresh.getExpense(4).description, "=SUM(A1)")

    def testImportSkipsBadRows(self):
        path = os.path.join(self.folder.name, "in.csv")
        with open(path, "w") as newFile:
            newFile.write("date,category,description,amount\n2026-09-01,food,Tea,10\nbad,food,Tea,10\n2026-09-01,food,Tea,-3\n")
        fresh = ExpenseManager(JsonStorage(os.path.join(self.folder.name, "fresh.json")))
        message = importCsv(fresh, path)
        self.assertIn("Imported 1 expenses", message)
        self.assertIn("Skipped 2 rows", message)

    def testImportRejectsWrongColumns(self):
        path = os.path.join(self.folder.name, "wrong.csv")
        with open(path, "w") as newFile:
            newFile.write("a,b\n1,2\n")
        with self.assertRaises(ValueError):
            importCsv(self.expenses, path)

    def testSafeCellHelpers(self):
        self.assertEqual(undoSafeCell(makeSafeCell("@cmd")), "@cmd")
        self.assertEqual(makeSafeCell("Lunch"), "Lunch")


if __name__ == "__main__":
    unittest.main()
