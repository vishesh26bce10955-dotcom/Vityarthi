import csv

from tracker.Logger import getLogger

FIELDS = ["date", "category", "description", "amount"]
FORMULA_STARTS = ("=", "+", "-", "@")


# 1. Stop spreadsheet programs from running text as a formula
def makeSafeCell(text: str) -> str:
    if text.startswith(FORMULA_STARTS):
        return f"'{text}"
    return text


# 2. Undo makeSafeCell when reading a file back in
def undoSafeCell(text: str) -> str:
    if text.startswith("'") and text[1:].startswith(FORMULA_STARTS):
        return text[1:]
    return text


# 3. Export expenses to a CSV file
def exportCsv(expenses: list, fileName: str) -> str:
    with open(fileName, "w", newline="", encoding="utf-8") as newFile:
        writer = csv.DictWriter(newFile, fieldnames=FIELDS)
        writer.writeheader()
        for expense in expenses:
            writer.writerow({"date": expense.date, "category": makeSafeCell(expense.category),
                             "description": makeSafeCell(expense.description), "amount": expense.amount})
    getLogger().info(f"Exported {len(expenses)} expenses to {fileName}.")
    return f"Exported {len(expenses)} expenses to {fileName}."


# 4. Import expenses from a CSV file, skipping bad rows
def importCsv(expenseManager, fileName: str) -> str:
    imported = 0
    errors = []
    with open(fileName, "r", newline="", encoding="utf-8") as newFile:
        reader = csv.DictReader(newFile)
        if not reader.fieldnames or not set(FIELDS).issubset(reader.fieldnames):
            raise ValueError(f"CSV file must have the columns: {', '.join(FIELDS)}.")
        for lineNumber, row in enumerate(reader, start=2):
            try:
                expenseManager.addExpense(row["amount"], undoSafeCell(row["category"]),
                                          undoSafeCell(row["description"]), row["date"])
                imported += 1
            except ValueError as e:
                errors.append(f"Line {lineNumber}: {e}")
    getLogger().info(f"Imported {imported} expenses from {fileName} with {len(errors)} errors.")
    message = f"Imported {imported} expenses from {fileName}."
    if errors:
        message += f"\nSkipped {len(errors)} rows:\n" + "\n".join(errors)
    return message
