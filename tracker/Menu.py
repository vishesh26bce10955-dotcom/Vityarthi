from datetime import date

from tracker.Budget_Manager import BudgetManager
from tracker.Csv_Transfer import exportCsv, importCsv
from tracker.Expense_Manager import ExpenseManager
from tracker.Reports import categoryChart, monthlySummary, monthlyTrend, topExpenses
from tracker.Storage import JsonStorage
from tracker.Validators import validateId

DATA_FILE = "data/expenses.json"
TABLE_HEADER = f"{'ID':>4} | {'Date':<10} | {'Category':<15} | {'Description':<30} | {'Amount':>10}"


# 1. Turn a list of expenses into a printable table
def formatTable(expenses: list) -> str:
    if not expenses:
        return "No expenses found."
    return "\n".join([TABLE_HEADER, "-" * len(TABLE_HEADER)] + [str(expense) for expense in expenses])


# 2. Ask for a date and use today when the user presses Enter
def askDate(prompt: str) -> str:
    return input(f"{prompt} (YYYY-MM-DD, Enter for today): ").strip() or date.today().isoformat()


# 3. Ask for a month and use the current month when the user presses Enter
def askMonth() -> str:
    return input("Enter month (YYYY-MM, Enter for this month): ").strip() or date.today().strftime("%Y-%m")


# 4. Expense management menu
def expenseMenu(expenseManager: ExpenseManager) -> str:
    ch = int(input("1. Add expense\n2. View all expenses\n3. Update expense\n4. Delete expense\n5. Search expenses\nEnter your choice: "))
    match ch:
        case 1:
            amount = input("Enter amount: ")
            category = input("Enter category: ")
            description = input("Enter description: ")
            return expenseManager.addExpense(amount, category, description, askDate("Enter date"))
        case 2:
            return formatTable(expenseManager.listExpenses())
        case 3:
            expenseId = validateId(input("Enter the ID of the expense to update: "))
            print(expenseManager.getExpense(expenseId))
            return expenseManager.updateExpense(expenseId, input("New amount (Enter to keep): "), input("New category (Enter to keep): "),
                                                input("New description (Enter to keep): "), input("New date (Enter to keep): "))
        case 4:
            expenseId = validateId(input("Enter the ID of the expense to delete: "))
            if input(f"Delete expense {expenseId}? (y/n): ").strip().lower() != "y":
                return "Deletion cancelled."
            return expenseManager.deleteExpense(expenseId)
        case 5:
            print("Leave a filter empty to skip it.")
            results = expenseManager.searchExpenses(input("Keyword in description: "), input("Category: "), input("From date (YYYY-MM-DD): "),
                                                    input("To date (YYYY-MM-DD): "), input("Minimum amount: "), input("Maximum amount: "))
            return formatTable(results)
        case _:
            return "Invalid choice!"


# 5. Budget management menu
def budgetMenu(budgetManager: BudgetManager) -> str:
    ch = int(input("1. Set budget\n2. Remove budget\n3. View budget status\nEnter your choice: "))
    match ch:
        case 1:
            return budgetManager.setBudget(input("Enter category: "), input("Enter monthly limit: "))
        case 2:
            return budgetManager.removeBudget(input("Enter category: "))
        case 3:
            month = askMonth()
            status = budgetManager.budgetStatus(month)
            if not status:
                return "No budgets have been set."
            lines = [f"Budget status for {month}"]
            for category, limit, spent, percent, label in status:
                lines.append(f"{category:<15.15} {spent:>10} / {limit:<10} {percent:>6}%  {label}")
            return "\n".join(lines)
        case _:
            return "Invalid choice!"


# 6. Reports menu
def reportMenu(expenseManager: ExpenseManager) -> str:
    ch = int(input("1. Monthly summary\n2. Spending by category\n3. Top 5 expenses\n4. Monthly trend\nEnter your choice: "))
    expenses = expenseManager.listExpenses()
    match ch:
        case 1:
            return monthlySummary(expenses, askMonth())
        case 2:
            return categoryChart(expenses)
        case 3:
            return formatTable(topExpenses(expenses))
        case 4:
            return monthlyTrend(expenses)
        case _:
            return "Invalid choice!"


# 7. Import and export menu
def transferMenu(expenseManager: ExpenseManager) -> str:
    ch = int(input("1. Export to CSV\n2. Import from CSV\nEnter your choice: "))
    match ch:
        case 1:
            return exportCsv(expenseManager.listExpenses(), input("Enter file name to export to: ").strip() or "expenses_export.csv")
        case 2:
            return importCsv(expenseManager, input("Enter file name to import from: ").strip())
        case _:
            return "Invalid choice!"


# 8. Main menu that starts the program
def mainMenu() -> str:
    storage = JsonStorage(DATA_FILE)
    expenseManager = ExpenseManager(storage)
    budgetManager = BudgetManager(storage, expenseManager)
    for alert in budgetManager.budgetAlerts(date.today().strftime("%Y-%m")):
        print(alert)
    while True:
        try:
            ch = int(input("\n===== Expense Tracker =====\n1. Expenses\n2. Budgets\n3. Reports\n4. Import / Export\n5. Exit\nEnter your choice: "))
            match ch:
                case 1: print(expenseMenu(expenseManager))
                case 2: print(budgetMenu(budgetManager))
                case 3: print(reportMenu(expenseManager))
                case 4: print(transferMenu(expenseManager))
                case 5: return "Goodbye! Keep tracking those expenses!"
                case _: print("Invalid choice!")
        except (ValueError, OSError) as e:
            print(f"An error occurred: {e}")
            storage.logger.warning(f"Menu error: {e}")
        except (KeyboardInterrupt, EOFError):
            return "\nGoodbye! Keep tracking those expenses!"
