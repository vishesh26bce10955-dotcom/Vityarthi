# Problem Statement

## Problem

Students and young professionals often have no clear picture of where their money goes. Spending is scattered across UPI apps, cash and cards, and by the time the month ends the budget is already gone. Spreadsheets are tedious to keep tidy and give no warning while there is still time to act, and full finance apps ask for accounts, sign-ups and internet access that many users do not want.

Pocket Ledger solves this with a small offline tool that records expenses quickly, checks them against monthly category budgets, warns before a limit is crossed, and explains the month with simple reports.

## Scope

**In scope**

- Recording, viewing, editing, deleting and searching personal expenses
- Monthly budgets per category with warning and over-budget alerts
- Monthly summary, category breakdown, top expenses and monthly trend reports
- CSV import and export
- Local JSON storage, input validation, error handling and an activity log
- A command-line interface

**Out of scope**

- Multiple users, logins or cloud sync
- Income tracking, bank integration or automatic SMS/UPI reading
- Multiple currencies
- A graphical or web interface

## Target users

- College students managing a monthly allowance
- Young professionals who want a private, no-account way to track spending
- Anyone comfortable running a Python program in a terminal

## High-level features

1. **Expense management:** add, list, update, delete and search expenses.
2. **Budgets and alerts:** per-category monthly limits, with `OK`, `WARNING` (80% or more) and `OVER BUDGET` status shown when the program starts and on request.
3. **Reports and analytics:** monthly summary, spending by category chart, top 5 expenses, monthly trend.
4. **Import / export:** move data in and out through CSV files, with bad rows skipped and reported.
5. **Reliability and safety:** exact decimal money, strict validation, atomic saves, recovery from a corrupted data file, logging.
