from decimal import Decimal

from tracker.Storage import JsonStorage
from tracker.Validators import validateAmount, validateCategory, validateMonth

WARNING_PERCENT = Decimal("80")


# Monthly budget limits per category
class BudgetManager:
    def __init__(self, storage: JsonStorage, expenseManager):
        self.storage = storage
        self.expenseManager = expenseManager
        self.logger = storage.logger

    def setBudget(self, category: str, amount: str) -> str:
        category = validateCategory(category)
        limit = validateAmount(amount)
        self.storage.data["budgets"][category] = str(limit)
        self.storage.save()
        self.logger.info(f"Budget for {category} set to {limit}.")
        return f"Monthly budget for {category} set to {limit}."

    def removeBudget(self, category: str) -> str:
        category = validateCategory(category)
        if category not in self.storage.data["budgets"]:
            raise ValueError(f"No budget found for {category}.")
        del self.storage.data["budgets"][category]
        self.storage.save()
        self.logger.info(f"Budget for {category} removed.")
        return f"Budget for {category} removed."

    def listBudgets(self) -> dict:
        return {category: Decimal(limit) for category, limit in self.storage.data["budgets"].items()}

    def spentInMonth(self, category: str, month: str) -> Decimal:
        month = validateMonth(month)
        return sum((expense.amount for expense in self.expenseManager.listExpenses()
                    if expense.category == category and expense.date.startswith(month)), Decimal("0"))

    def budgetStatus(self, month: str) -> list:
        status = []
        for category, limit in sorted(self.listBudgets().items()):
            spent = self.spentInMonth(category, month)
            percent = (spent / limit * 100).quantize(Decimal("0.1"))
            if spent > limit:
                label = "OVER BUDGET"
            elif percent >= WARNING_PERCENT:
                label = "WARNING"
            else:
                label = "OK"
            status.append((category, limit, spent, percent, label))
        return status

    def budgetAlerts(self, month: str) -> list:
        return [f"{label}: {category} has used {percent}% of its budget ({spent} of {limit})."
                for category, limit, spent, percent, label in self.budgetStatus(month) if label != "OK"]
