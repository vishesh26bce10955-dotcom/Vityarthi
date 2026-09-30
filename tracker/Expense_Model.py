from decimal import Decimal


# Expense record
class Expense:
    def __init__(self, expenseId: int, amount: Decimal, category: str, description: str, date: str):
        self.expenseId = expenseId
        self.amount = amount
        self.category = category
        self.description = description
        self.date = date

    def toDict(self) -> dict:
        return {
            "id": self.expenseId,
            "amount": str(self.amount),
            "category": self.category,
            "description": self.description,
            "date": self.date
        }

    @staticmethod
    def fromDict(data: dict) -> "Expense":
        return Expense(int(data["id"]), Decimal(data["amount"]), data["category"], data["description"], data["date"])

    def __str__(self) -> str:
        return f"{self.expenseId:>4} | {self.date} | {self.category:<15.15} | {self.description:<30.30} | {self.amount:>10}"
