from decimal import Decimal

from tracker.Validators import validateMonth

BAR_WIDTH = 30


# 1. Total amount of a list of expenses
def totalAmount(expenses: list) -> Decimal:
    return sum((expense.amount for expense in expenses), Decimal("0"))


# 2. Group expense totals by category
def categoryTotals(expenses: list) -> dict:
    totals = {}
    for expense in expenses:
        if expense.category in totals:
            totals[expense.category] += expense.amount
        else:
            totals[expense.category] = expense.amount
    return dict(sorted(totals.items(), key=lambda item: item[1], reverse=True))


# 3. Draw a text bar chart of category totals
def categoryChart(expenses: list) -> str:
    totals = categoryTotals(expenses)
    if not totals:
        return "No expenses to chart."
    highest = max(totals.values())
    lines = []
    for category, amount in totals.items():
        bar = "#" * max(1, int(amount / highest * BAR_WIDTH))
        lines.append(f"{category:<15.15} | {bar} {amount}")
    return "\n".join(lines)


# 4. Summary of one month with category breakdown
def monthlySummary(expenses: list, month: str) -> str:
    month = validateMonth(month)
    monthExpenses = [expense for expense in expenses if expense.date.startswith(month)]
    if not monthExpenses:
        return f"No expenses found for {month}."
    total = totalAmount(monthExpenses)
    average = (total / len(monthExpenses)).quantize(Decimal("0.01"))
    lines = [f"Summary for {month}", f"Expenses: {len(monthExpenses)}", f"Total spent: {total}", f"Average expense: {average}", ""]
    for category, amount in categoryTotals(monthExpenses).items():
        share = (amount / total * 100).quantize(Decimal("0.1"))
        lines.append(f"{category:<15.15} {amount:>10} ({share}%)")
    return "\n".join(lines)


# 5. The most expensive expenses
def topExpenses(expenses: list, count: int = 5) -> list:
    if count <= 0:
        raise ValueError("Count must be greater than zero.")
    return sorted(expenses, key=lambda expense: expense.amount, reverse=True)[:count]


# 6. Total spent in each month, oldest first
def monthlyTrend(expenses: list) -> str:
    if not expenses:
        return "No expenses to show a trend for."
    totals = {}
    for expense in expenses:
        month = expense.date[:7]
        totals[month] = totals.get(month, Decimal("0")) + expense.amount
    highest = max(totals.values())
    lines = []
    for month, amount in sorted(totals.items()):
        bar = "#" * max(1, int(amount / highest * BAR_WIDTH))
        lines.append(f"{month} | {bar} {amount}")
    return "\n".join(lines)
