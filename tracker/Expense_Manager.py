from decimal import Decimal

from tracker.Expense_Model import Expense
from tracker.Storage import JsonStorage
from tracker.Validators import validateAmount, validateCategory, validateDate, validateDescription


# Create, read, update and delete expenses
class ExpenseManager:
    def __init__(self, storage: JsonStorage):
        self.storage = storage
        self.logger = storage.logger

    def addExpense(self, amount: str, category: str, description: str, date: str) -> str:
        expense = Expense(self.storage.data["nextId"], validateAmount(amount), validateCategory(category),
                          validateDescription(description), validateDate(date))
        self.storage.data["expenses"].append(expense.toDict())
        self.storage.data["nextId"] += 1
        self.storage.save()
        self.logger.info(f"Added expense {expense.expenseId}: {expense.amount} in {expense.category}.")
        return f"Expense added with ID {expense.expenseId}."

    def listExpenses(self) -> list:
        expenses = [Expense.fromDict(item) for item in self.storage.data["expenses"]]
        return sorted(expenses, key=lambda expense: (expense.date, expense.expenseId))

    def getExpense(self, expenseId: int) -> Expense:
        for item in self.storage.data["expenses"]:
            if item["id"] == expenseId:
                return Expense.fromDict(item)
        raise ValueError(f"No expense found with ID {expenseId}.")

    def updateExpense(self, expenseId: int, amount: str = "", category: str = "", description: str = "", date: str = "") -> str:
        expense = self.getExpense(expenseId)
        if amount:
            expense.amount = validateAmount(amount)
        if category:
            expense.category = validateCategory(category)
        if description:
            expense.description = validateDescription(description)
        if date:
            expense.date = validateDate(date)
        for i, item in enumerate(self.storage.data["expenses"]):
            if item["id"] == expenseId:
                self.storage.data["expenses"][i] = expense.toDict()
        self.storage.save()
        self.logger.info(f"Updated expense {expenseId}.")
        return f"Expense {expenseId} updated."

    def deleteExpense(self, expenseId: int) -> str:
        self.getExpense(expenseId)
        self.storage.data["expenses"] = [item for item in self.storage.data["expenses"] if item["id"] != expenseId]
        self.storage.save()
        self.logger.info(f"Deleted expense {expenseId}.")
        return f"Expense {expenseId} deleted."

    def searchExpenses(self, keyword: str = "", category: str = "", startDate: str = "", endDate: str = "",
                       minAmount: str = "", maxAmount: str = "") -> list:
        results = self.listExpenses()
        if keyword:
            results = [expense for expense in results if keyword.lower() in expense.description.lower()]
        if category:
            results = [expense for expense in results if expense.category == validateCategory(category)]
        if startDate:
            results = [expense for expense in results if expense.date >= validateDate(startDate)]
        if endDate:
            results = [expense for expense in results if expense.date <= validateDate(endDate)]
        if minAmount:
            results = [expense for expense in results if expense.amount >= Decimal(minAmount)]
        if maxAmount:
            results = [expense for expense in results if expense.amount <= Decimal(maxAmount)]
        return results

    def listCategories(self) -> list:
        return sorted({expense.category for expense in self.listExpenses()})
