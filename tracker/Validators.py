from datetime import date
from decimal import Decimal, InvalidOperation

MAX_AMOUNT = Decimal("10000000")
MAX_TEXT_LENGTH = 60


# 1. Convert text into a valid positive money amount
def validateAmount(text: str) -> Decimal:
    try:
        amount = Decimal(text.strip())
    except InvalidOperation:
        raise ValueError(f"'{text}' is not a valid amount.")
    if not amount.is_finite():
        raise ValueError("Amount must be a finite number.")
    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")
    if amount > MAX_AMOUNT:
        raise ValueError(f"Amount cannot be more than {MAX_AMOUNT}.")
    return amount.quantize(Decimal("0.01"))


# 2. Check that a date is written as YYYY-MM-DD and is not in the future
def validateDate(text: str) -> str:
    try:
        parsedDate = date.fromisoformat(text.strip())
    except ValueError:
        raise ValueError(f"'{text}' is not a valid date. Use the format YYYY-MM-DD.")
    if parsedDate > date.today():
        raise ValueError("Date cannot be in the future.")
    return parsedDate.isoformat()


# 3. Check that a month is written as YYYY-MM
def validateMonth(text: str) -> str:
    try:
        year, month = text.strip().split("-")
        parsedDate = date(int(year), int(month), 1)
    except ValueError:
        raise ValueError(f"'{text}' is not a valid month. Use the format YYYY-MM.")
    return parsedDate.strftime("%Y-%m")


# 4. Clean a category name and make sure it is usable
def validateCategory(text: str) -> str:
    category = " ".join(text.split()).title()
    if not category:
        raise ValueError("Category cannot be empty.")
    if len(category) > MAX_TEXT_LENGTH:
        raise ValueError(f"Category cannot be longer than {MAX_TEXT_LENGTH} characters.")
    return category


# 5. Clean a description and make sure it is usable
def validateDescription(text: str) -> str:
    description = " ".join(text.split())
    if not description:
        raise ValueError("Description cannot be empty.")
    if len(description) > MAX_TEXT_LENGTH:
        raise ValueError(f"Description cannot be longer than {MAX_TEXT_LENGTH} characters.")
    return description


# 6. Read a positive whole number such as an expense ID
def validateId(text: str) -> int:
    try:
        num = int(text.strip())
    except ValueError:
        raise ValueError(f"'{text}' is not a valid ID.")
    if num <= 0:
        raise ValueError("ID must be a positive number.")
    return num
