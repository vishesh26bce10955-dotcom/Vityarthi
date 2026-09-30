import os

from PIL import Image as PilImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, CondPageBreak, Frame, Image, KeepTogether, NextPageTemplate, PageBreak,
                                PageTemplate, Paragraph, Spacer, Table, TableStyle)
from reportlab.platypus.flowables import HRFlowable
from reportlab.platypus.tableofcontents import TableOfContents

DOCS = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
IMAGES = os.path.join(DOCS, "images")
OUTPUT = os.path.join(DOCS, "Expense_Tracker_Report.pdf")
FONT_FOLDER = "C:/Windows/Fonts"

NAVY = colors.HexColor("#0F172A")
INK = colors.HexColor("#1E293B")
MUTED = colors.HexColor("#64748B")
ACCENT = colors.HexColor("#0D9488")
SOFT = colors.HexColor("#F1F5F9")
LINE = colors.HexColor("#E2E8F0")

PAGE_W, PAGE_H = A4
MARGIN = 2.2 * cm
CONTENT_W = PAGE_W - 2 * MARGIN
COVER_META = [("STUDENT", "[Your name]"), ("REGISTRATION NO.", "[Your registration number]"),
              ("COURSE", "[Course name and code]"), ("FACULTY", "[Faculty name]"), ("SUBMITTED", "[Date]")]


# 1. Register the fonts used in the report
def registerFonts() -> None:
    fonts = {"Seg": "segoeui.ttf", "Seg-Bold": "segoeuib.ttf", "Seg-Italic": "segoeuii.ttf", "Seg-BoldItalic": "segoeuiz.ttf",
             "Seg-Semi": "seguisb.ttf", "Seg-Light": "segoeuil.ttf", "Mono": "consola.ttf"}
    for name, fileName in fonts.items():
        pdfmetrics.registerFont(TTFont(name, os.path.join(FONT_FOLDER, fileName)))
    pdfmetrics.registerFontFamily("Seg", normal="Seg", bold="Seg-Bold", italic="Seg-Italic", boldItalic="Seg-BoldItalic")


registerFonts()

body = ParagraphStyle("body", fontName="Seg", fontSize=10, leading=15.5, textColor=INK, spaceAfter=7)
small = ParagraphStyle("small", parent=body, fontSize=8.5, leading=12, textColor=MUTED, spaceAfter=0)
bulletStyle = ParagraphStyle("bullet", parent=body, leftIndent=14, bulletIndent=1, spaceAfter=3)
kicker = ParagraphStyle("kicker", fontName="Seg-Bold", fontSize=8, leading=10, textColor=ACCENT, spaceBefore=4, spaceAfter=2)
sectionTitle = ParagraphStyle("SecTitle", fontName="Seg-Bold", fontSize=25, leading=30, textColor=NAVY, spaceAfter=6)
subTitle = ParagraphStyle("sub", fontName="Seg-Semi", fontSize=12.5, leading=17, textColor=NAVY, spaceBefore=12, spaceAfter=5)
cellStyle = ParagraphStyle("cell", fontName="Seg", fontSize=9, leading=12.5, textColor=INK)
headStyle = ParagraphStyle("head", fontName="Seg-Bold", fontSize=7.5, leading=10, textColor=MUTED)
captionStyle = ParagraphStyle("caption", fontName="Seg", fontSize=8.5, leading=12, textColor=MUTED, alignment=TA_CENTER, spaceBefore=6, spaceAfter=10)
quoteStyle = ParagraphStyle("quote", fontName="Seg-Light", fontSize=13, leading=20, textColor=NAVY)


# 2. Section heading that also feeds the table of contents
class SectionHeading(Paragraph):
    def __init__(self, number: str, title: str):
        super().__init__(title, sectionTitle)
        self.tocText = f"<font name='Seg-Bold' color='#0D9488'>{number}</font>&nbsp;&nbsp;&nbsp;{title}"


class ReportDoc(BaseDocTemplate):
    def afterFlowable(self, flowable) -> None:
        if isinstance(flowable, SectionHeading):
            self.notify("TOCEntry", (0, flowable.tocText, self.page))


# 3. A section opening: small label, big title, short accent rule
def section(number: str, title: str, newPage: bool = True) -> list:
    opening = [PageBreak()] if newPage else [CondPageBreak(7 * cm), Spacer(1, 14)]
    return opening + [Paragraph(f"SECTION {number}", kicker), SectionHeading(number, title),
                      HRFlowable(width=1.1 * cm, thickness=2.5, color=ACCENT, hAlign="LEFT", spaceAfter=14)]


# 4. Body text and bullet helpers
def para(text: str) -> Paragraph:
    return Paragraph(text, body)


def bullets(items: list) -> list:
    return [Paragraph(item, bulletStyle, bulletText="•") for item in items]


def sub(text: str) -> Paragraph:
    return Paragraph(text, subTitle)


# 5. Clean table: no vertical lines, hairline rows, muted header
def cleanTable(rows: list, widths: list) -> Table:
    data = [[Paragraph(text.upper(), headStyle) for text in rows[0]]]
    data += [[Paragraph(str(text), cellStyle) for text in row] for row in rows[1:]]
    result = Table(data, colWidths=widths, repeatRows=1)
    result.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, 0), 1, NAVY), ("LINEBELOW", (0, 1), (-1, -1), 0.5, LINE),
                                ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 6),
                                ("BOTTOMPADDING", (0, 0), (-1, -1), 6), ("LEFTPADDING", (0, 0), (-1, -1), 4)]))
    return result


# 6. Row of big-number cards
def statCards(items: list) -> Table:
    gap = 0.35 * cm
    width = (CONTENT_W - gap * (len(items) - 1)) / len(items)
    cells = []
    widths = []
    for i, (number, label) in enumerate(items):
        card = Table([[Paragraph(number, ParagraphStyle("n", fontName="Seg-Bold", fontSize=26, leading=30, textColor=ACCENT))],
                      [Paragraph(label, ParagraphStyle("l", fontName="Seg", fontSize=8.5, leading=11, textColor=MUTED))]], colWidths=[width])
        card.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), SOFT), ("LEFTPADDING", (0, 0), (-1, -1), 12),
                                  ("TOPPADDING", (0, 0), (0, 0), 12), ("BOTTOMPADDING", (0, -1), (-1, -1), 12)]))
        cells.append(card)
        widths.append(width)
        if i < len(items) - 1:
            cells.append("")
            widths.append(gap)
    row = Table([cells], colWidths=widths)
    row.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                             ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    return row


# 7. Highlighted statement with a teal edge
def callout(text: str, style: ParagraphStyle = quoteStyle) -> Table:
    box = Table([["", Paragraph(text, style)]], colWidths=[0.12 * cm, CONTENT_W - 0.12 * cm])
    box.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, 0), ACCENT), ("BACKGROUND", (1, 0), (1, 0), SOFT),
                             ("LEFTPADDING", (1, 0), (1, 0), 16), ("RIGHTPADDING", (1, 0), (1, 0), 16),
                             ("TOPPADDING", (0, 0), (-1, -1), 14), ("BOTTOMPADDING", (0, 0), (-1, -1), 14)]))
    return box


# 8. Picture scaled to fit, on a soft card, with a caption
def picture(fileName: str, text: str, maxWidth: float = CONTENT_W, maxHeight: float = 19 * cm) -> list:
    width, height = PilImage.open(os.path.join(IMAGES, fileName)).size
    scale = min((maxWidth - 28) / width, maxHeight / height)
    card = Table([[Image(os.path.join(IMAGES, fileName), width * scale, height * scale)]], colWidths=[CONTENT_W])
    card.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.5, LINE), ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                              ("TOPPADDING", (0, 0), (-1, -1), 14), ("BOTTOMPADDING", (0, 0), (-1, -1), 14)]))
    return [card, Paragraph(text, captionStyle)]


# 9. Screenshot with a short explanation beside it
def shotRow(label: str, title: str, text: str, fileName: str, caption: str) -> KeepTogether:
    width, height = PilImage.open(os.path.join(IMAGES, fileName)).size
    scale = min(10.4 * cm / width, 11.2 * cm / height)
    words = [Paragraph(label, kicker), Paragraph(title, ParagraphStyle("st", fontName="Seg-Semi", fontSize=13, leading=17, textColor=NAVY, spaceAfter=6)),
             Paragraph(text, ParagraphStyle("sb", parent=body, fontSize=9.5, leading=14)), Paragraph(caption, small)]
    row = Table([[words, Image(os.path.join(IMAGES, fileName), width * scale, height * scale)]],
                colWidths=[CONTENT_W - 10.8 * cm, 10.8 * cm])
    row.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (0, 0), 0), ("RIGHTPADDING", (0, 0), (0, 0), 14),
                             ("ALIGN", (1, 0), (1, 0), "RIGHT"), ("RIGHTPADDING", (1, 0), (1, 0), 0)]))
    return KeepTogether([row, Spacer(1, 16)])


# 10. Cover page drawn straight onto the canvas
def drawCover(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    canvas.setFillColor(ACCENT)
    canvas.setFillAlpha(0.16)
    canvas.circle(PAGE_W - 1.5 * cm, PAGE_H - 4 * cm, 7.5 * cm, stroke=0, fill=1)
    canvas.setFillAlpha(0.10)
    canvas.circle(PAGE_W - 6 * cm, PAGE_H - 9.5 * cm, 4 * cm, stroke=0, fill=1)
    canvas.setFillAlpha(1)
    canvas.setFillColor(ACCENT)
    canvas.rect(MARGIN, PAGE_H - 12.3 * cm, 1.6 * cm, 0.14 * cm, stroke=0, fill=1)
    canvas.setFillColor(colors.HexColor("#5EEAD4"))
    canvas.setFont("Seg-Bold", 9)
    canvas.drawString(MARGIN, PAGE_H - 11.4 * cm, "PROJECT REPORT")
    canvas.setFillColor(colors.white)
    canvas.setFont("Seg-Bold", 46)
    canvas.drawString(MARGIN, PAGE_H - 14.4 * cm, "Pocket Ledger")
    canvas.setFillColor(colors.HexColor("#CBD5E1"))
    canvas.setFont("Seg-Light", 16)
    canvas.drawString(MARGIN, PAGE_H - 15.7 * cm, "A private, offline expense tracker in Python")
    y = 8.6 * cm
    for label, value in COVER_META:
        canvas.setFillColor(colors.HexColor("#5EEAD4"))
        canvas.setFont("Seg-Bold", 7.5)
        canvas.drawString(MARGIN, y, label)
        canvas.setFillColor(colors.white)
        canvas.setFont("Seg", 11)
        canvas.drawString(MARGIN + 4.2 * cm, y, value)
        y -= 0.85 * cm
    canvas.setFillColor(colors.HexColor("#64748B"))
    canvas.setFont("Seg", 8)
    canvas.drawString(MARGIN, 1.6 * cm, "VITyarthi  |  Build Your Own Project")
    canvas.restoreState()


# 11. Running header and page number for the inside pages
def drawPage(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Seg-Bold", 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(MARGIN, PAGE_H - 1.3 * cm, "POCKET LEDGER")
    canvas.setFont("Seg", 7)
    canvas.drawRightString(PAGE_W - MARGIN, PAGE_H - 1.3 * cm, "Project Report")
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.6)
    canvas.line(MARGIN, PAGE_H - 1.5 * cm, PAGE_W - MARGIN, PAGE_H - 1.5 * cm)
    canvas.setFont("Seg-Bold", 8)
    canvas.setFillColor(ACCENT)
    canvas.drawRightString(PAGE_W - MARGIN, 1.2 * cm, f"{doc.page:02d}")
    canvas.restoreState()


# 12. Assemble the whole report
def buildReport() -> None:
    doc = ReportDoc(OUTPUT, pagesize=A4, title="Pocket Ledger: Expense Tracker Project Report", author="[Your name]")
    doc.addPageTemplates([
        PageTemplate("Cover", [Frame(0, 0, PAGE_W, PAGE_H, id="cover")], onPage=drawCover),
        PageTemplate("Body", [Frame(MARGIN, 1.9 * cm, CONTENT_W, PAGE_H - 4.2 * cm, id="body", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)],
                     onPage=drawPage)])
    s = [NextPageTemplate("Body"), Spacer(1, 1), PageBreak()]

    toc = TableOfContents()
    toc.dotsMinLevel = -1
    toc.levelStyles = [ParagraphStyle("toc0", fontName="Seg", fontSize=11.5, leading=27, textColor=INK, rightIndent=0)]
    s += [Paragraph("CONTENTS", kicker), Paragraph("What's inside", sectionTitle), HRFlowable(width=1.1 * cm, thickness=2.5, color=ACCENT, hAlign="LEFT", spaceAfter=16), toc]

    s += section("01", "Introduction")
    s += [para("Pocket Ledger is a personal expense tracker that runs in the terminal. It is built for people who want to understand where their money "
               "goes without creating accounts, installing large apps or sending financial data to anyone. Every expense is recorded with an amount, "
               "category, description and date, compared against monthly budgets, and turned into simple summaries. It applies core Python ideas "
               "(type-hinted functions, classes, file handling, exceptions, comprehensions, modular design) and adds tests, logging and documentation."),
          Spacer(1, 6),
          statCards([("4", "functional modules"), ("9", "Python modules"), ("28", "unit tests, all passing"), ("0", "external dependencies")])]

    s += section("02", "Problem Statement", newPage=False)
    s += [callout("Most people know what they earn but not where it goes. Pocket Ledger is a small offline tool that records spending quickly, "
                  "warns before a budget is crossed, and explains the month in plain reports."),
          Spacer(1, 4),
          sub("Objectives")]
    s += bullets(["Record, view, edit, delete and search expenses with strict input validation.",
                  "Set monthly budgets per category and get OK, WARNING and OVER BUDGET status automatically.",
                  "Provide a monthly summary, category chart, top expenses and monthly trend.",
                  "Support CSV import and export with clear reporting of bad rows.",
                  "Never lose or corrupt data, and keep a log of what the program does."])
    s += [sub("Scope and target users"),
          cleanTable([["In scope", "Out of scope", "Target users"],
                      ["Single-user expense tracking, budgets and alerts, reports, CSV transfer, local JSON storage, command-line interface.",
                       "Multiple users, cloud sync, bank or UPI integration, income tracking, multiple currencies, graphical interface.",
                       "College students and young professionals who are comfortable running a Python program."]],
                     [CONTENT_W / 3] * 3)]

    s += section("03", "Functional Requirements")
    s += [para("Four modules, all driven from one numbered menu. Every module takes typed input, validates it and returns a clear message."),
          Spacer(1, 4),
          cleanTable([["ID", "Module", "Requirement"],
                      ["FR1", "Expenses", "Add an expense with amount, category, description and date (date defaults to today)."],
                      ["FR2", "Expenses", "View all expenses in a table sorted by date."],
                      ["FR3", "Expenses", "Update any field of an expense by ID; blank input keeps the old value."],
                      ["FR4", "Expenses", "Delete an expense by ID after confirmation."],
                      ["FR5", "Expenses", "Search by keyword, category, date range and amount range, alone or combined."],
                      ["FR6", "Budgets", "Set or remove a monthly budget for a category."],
                      ["FR7", "Budgets", "Show status per category: OK, WARNING (80% or more used) or OVER BUDGET."],
                      ["FR8", "Budgets", "Show alerts automatically when the program starts."],
                      ["FR9", "Reports", "Monthly summary: count, total, average and category share."],
                      ["FR10", "Reports", "Text bar charts of spending by category and by month."],
                      ["FR11", "Reports", "List the five most expensive expenses."],
                      ["FR12", "Import / export", "Export all expenses to CSV."],
                      ["FR13", "Import / export", "Import from CSV, skipping and reporting invalid rows."]],
                     [1.5 * cm, 3.2 * cm, CONTENT_W - 4.7 * cm]),
          sub("How a session flows"),
          para("On start the program loads the data file, recovers if it is corrupt, prints any budget alerts for the current month and shows the main "
               "menu. The user picks a module and answers the prompts. The input is validated, the operation runs, the file is saved and a result "
               "message is shown. Errors appear as messages and the user is returned to the menu; bad input never crashes the program.")]

    s += section("04", "Non-functional Requirements")
    s += [cleanTable([["Quality", "How it is met"],
                      ["Reliability", "Saves go to a temporary file and then replace the real file, so a crash cannot leave half a file. A corrupt file is renamed "
                                      "to <i>expenses.json.corrupt-timestamp</i> and the program starts clean instead of failing."],
                      ["Security", "All input passes through one validation module. Money is exact Decimal. CSV cells starting with =, +, - or @ are prefixed "
                                   "on export so spreadsheets do not run them as formulas. Data never leaves the machine. No eval."],
                      ["Usability", "Numbered menus, short prompts, friendly full-sentence messages, sensible defaults for date and month, "
                                    "confirmation before delete, alert summary at start-up."],
                      ["Error handling", "Validators raise ValueError with a clear message. The menu loop catches ValueError and OSError, prints "
                                         "'An error occurred: ...', logs a warning and carries on."],
                      ["Logging", "Every change and every error is written with timestamp and level to logs/expense_tracker.log."],
                      ["Maintainability", "Small typed functions, one job per module, validation written once, and a test suite that guards refactoring."],
                      ["Performance and efficiency", "Standard library only, no background work. Data is loaded once and cached; linear scans stay instant for thousands of records."],
                      ["Scalability", "Managers only need load and save from the storage class, so JSON can be swapped for SQLite without touching menus, reports or validation."]],
                     [3.6 * cm, CONTENT_W - 3.6 * cm])]

    s += section("05", "System Architecture")
    s += [para("The application has three layers plus shared helpers. The presentation layer talks only to the business layer, the business layer holds every "
               "rule, and only the data layer touches the file. Validation and logging are used by all layers."),
          Spacer(1, 4)]
    s += picture("architecture.png", "Figure 1. Layered architecture", maxHeight=10.5 * cm)
    s += [cleanTable([["File", "Responsibility"],
                      ["Main.py", "Entry point; prints the result of mainMenu()."],
                      ["tracker/Menu.py", "All menus and prompts; the only place that reads input or prints."],
                      ["tracker/Expense_Manager.py", "ExpenseManager: add, list, get, update, delete, search."],
                      ["tracker/Budget_Manager.py", "BudgetManager: budgets, monthly status and alerts."],
                      ["tracker/Reports.py", "Totals, category grouping, text charts, top expenses, trend."],
                      ["tracker/Csv_Transfer.py", "CSV export and import with formula protection."],
                      ["tracker/Expense_Model.py, Storage.py", "Expense class; JsonStorage with atomic saves and recovery."],
                      ["tracker/Validators.py, Logger.py", "Six validation functions; file logger."]],
                     [5.6 * cm, CONTENT_W - 5.6 * cm])]

    s += section("06", "Design Diagrams")
    s += [sub("Use case diagram"), para("One actor uses nine use cases. Adding, updating and importing all include input validation."), Spacer(1, 4)]
    s += picture("use_case.png", "Figure 2. Use case diagram", maxHeight=14 * cm)
    s += [PageBreak(), sub("Workflow diagram"), Spacer(1, 4)]
    s += picture("workflow.png", "Figure 3. Workflow of a user session", maxHeight=20 * cm)
    s += [PageBreak(), sub("Sequence diagram: add an expense"),
          para("Validation, the atomic save, logging and the returned message, step by step."), Spacer(1, 4)]
    s += picture("sequence.png", "Figure 4. Sequence diagram", maxHeight=17 * cm)
    s += [PageBreak(), sub("Class and component diagram"), Spacer(1, 4)]
    s += picture("class_diagram.png", "Figure 5. Classes and modules", maxHeight=17 * cm)
    s += [PageBreak(), sub("ER diagram and storage schema"),
          para("All data lives in one JSON file. Amounts are stored as strings so decimal values stay exact. The link between budgets and expenses is "
               "the category name."), Spacer(1, 4)]
    s += picture("er_diagram.png", "Figure 6. ER diagram", maxHeight=8 * cm)
    s += [cleanTable([["Key", "Type", "Example"],
                      ["nextId", "integer", "15"],
                      ["expenses[ ]", "id, amount, category, description, date", "14, \"45.50\", \"Food\", \"Coffee with friends\", \"2026-09-29\""],
                      ["budgets{ }", "category: limit (strings)", "{\"Food\": \"1000.00\"}"]],
                     [3.2 * cm, 6 * cm, CONTENT_W - 9.2 * cm])]

    s += section("07", "Design Decisions and Rationale")
    s += [cleanTable([["Decision", "Why"],
                      ["Decimal, not float, for money", "Floats give errors like 0.1 + 0.2 = 0.30000000000000004. Decimal keeps every total exact."],
                      ["JSON file, not a database", "Small single-user data. JSON is readable, needs no setup and is easy to back up. The storage class hides it, so a database can replace it."],
                      ["Atomic save", "Writing to a temp file and then os.replace means a crash or power cut cannot corrupt the existing file."],
                      ["Managers return messages and raise ValueError", "Logic can be tested without any input or printing; only Menu.py talks to the user."],
                      ["One Validators module", "Rules live in one place and protect manual entry, updates and CSV import alike."],
                      ["Standard library only", "Runs anywhere Python 3.10+ is installed; nothing for the user to install."],
                      ["Text charts", "Work in any terminal and paste into reports; no plotting library needed."],
                      ["Future dates rejected", "Catches typing mistakes such as the wrong year and keeps monthly totals honest."],
                      ["Categories normalised to Title Case", "'food', 'Food ' and 'FOOD' become one category, so budgets and reports always match."]],
                     [5.4 * cm, CONTENT_W - 5.4 * cm])]

    s += section("08", "Implementation Details")
    s += [para("The code follows one consistent style: camelCase names, type hints on every function, guard clauses that raise ValueError with full-sentence "
               "messages, early returns, f-strings and a numbered header comment above each function. Functions return results and messages; only the "
               "menu layer prints."),
          sub("Concepts applied"),
          cleanTable([["Concept", "Where it is used"],
                      ["Classes and objects", "Expense, JsonStorage, ExpenseManager, BudgetManager"],
                      ["Exception handling", "ValueError in validators, try / except in the menu loop, storage recovery"],
                      ["File handling", "JSON and CSV with <i>with open(...)</i>, atomic writes, corrupt-file backup"],
                      ["Dictionaries and sets", "Category totals, monthly totals, unique categories"],
                      ["Comprehensions, lambda, sorted", "Search filters, sorting by date, amount and total"],
                      ["match / case", "Every menu"],
                      ["Standard library", "decimal, datetime, csv, json, logging, os, unittest"]],
                     [5 * cm, CONTENT_W - 5 * cm]),
          sub("Key algorithms")]
    s += bullets(["<b>Search.</b> Start from the sorted list and narrow it with one comprehension per filter that was supplied.",
                  "<b>Budget status.</b> spent = sum of the category's expenses in the month; percent = spent / limit x 100. "
                  "Over the limit is OVER BUDGET, 80% or more is WARNING, anything else is OK.",
                  "<b>Category totals.</b> One pass builds a dictionary; the items are then sorted highest first.",
                  "<b>Bar chart.</b> Bar length = amount / highest amount x 30 characters, never fewer than one.",
                  "<b>Atomic save.</b> Write <i>file.tmp</i>, then os.replace onto the real file."])

    s += section("09", "Screenshots and Results")
    s += [para("Captured by running the real program with scripted input on the sample data (docs/tools/make_screenshots.py). Each menu is shown once to keep the images short."),
          Spacer(1, 6)]
    s += [shotRow("IMPORT", "Load data from CSV", "The sample file has one future-dated row. It is skipped and reported by line number while the rest are imported.",
                  "shot_import.png", "Figure 7"),
          shotRow("ADD AND SEARCH", "Validation in action", "A bad amount is rejected with a clear message and the program carries on. A valid entry is saved, then found by keyword.",
                  "shot_add_search.png", "Figure 8"),
          shotRow("UPDATE AND DELETE", "Edit safely", "Blank answers keep the old values. Deleting asks for confirmation first.",
                  "shot_update_delete.png", "Figure 9"),
          shotRow("BUDGETS", "Status and start-up alerts", "Four budgets are set and September is checked. When the program restarts, the problem categories are shown immediately.",
                  "shot_budgets.png", "Figure 10"),
          shotRow("REPORTS", "Summary and category chart", "Totals, average and each category's share of the month, then a bar chart of spending by category.",
                  "shot_reports_summary.png", "Figure 11"),
          shotRow("REPORTS", "Top expenses and trend", "The five largest expenses and a month-by-month bar chart.",
                  "shot_reports_top_trend.png", "Figure 12"),
          shotRow("EXPORT", "Save to CSV", "All expenses are written to a spreadsheet-friendly file.", "shot_export.png", "Figure 13")]

    s += section("10", "Testing Approach")
    s += [para("Testing uses Python's built-in unittest. Every test creates its own temporary data folder, so tests never touch real data or each other."),
          cleanTable([["Test file", "What it covers"],
                      ["test_validators.py", "Amount rounding and rejection (text, zero, negative, NaN, Infinity, too large); date format and future dates; month, category, description and ID rules."],
                      ["test_expense_manager.py", "ID assignment, invalid input, persistence across restarts, partial updates, failed updates leaving data unchanged, delete, every search filter, corrupt-file recovery."],
                      ["test_budget_and_reports.py", "Budget labels and alerts, totals, monthly summary, top expenses, empty-data charts, CSV round trip with formula protection, bad-row skipping, wrong columns."]],
                     [5 * cm, CONTENT_W - 5 * cm]),
          Spacer(1, 10),
          callout("<b>28 tests, all passing.</b> Run <font name='Mono' size='9'>python -m unittest discover -s tests -t .</font>. The full menu flow was also "
                  "exercised end to end with scripted input, which confirmed that errors are shown and the program keeps running.", ParagraphStyle("cq", parent=body, fontSize=10.5, leading=16, spaceAfter=0))]

    s += section("11", "Challenges Faced", newPage=False)
    s += [Spacer(1, 4)]
    s += bullets(["<b>Money precision.</b> Float arithmetic showed rounding errors, so everything moved to Decimal, stored as strings in JSON.",
                  "<b>Lost messages.</b> Functions return messages instead of printing, so every caller had to be checked to make sure the message is shown.",
                  "<b>Menu after errors.</b> Returning from an error handler would end the program, so the loop prints the error and continues.",
                  "<b>Safe saving.</b> A plain write can corrupt the file if interrupted, which led to temp-file-and-replace and corrupt-file recovery.",
                  "<b>CSV safety.</b> Text starting with = or @ can run as a formula in a spreadsheet, so export and import guard against it.",
                  "<b>Month matching.</b> Comparing the YYYY-MM prefix of a date is simple but only safe because every date is validated to one format."])
    s += section("12", "Learnings and Key Takeaways", newPage=False)
    s += bullets(["Separating logic from input and output makes code far easier to test.",
                  "Validating in one place is safer than checking wherever data is used.",
                  "Early tests exposed edge cases, such as a failed update still changing data.",
                  "Designing for failure (corrupt file, bad CSV row, bad input) matters as much as the normal path.",
                  "Diagrams drawn during the work kept module boundaries clear."])
    s += section("13", "Future Enhancements", newPage=False)
    s += bullets(["Recurring expenses such as rent and subscriptions.",
                  "Income tracking and a savings-rate report.",
                  "SQLite storage behind the same storage interface.",
                  "A graphical or web front end reusing the manager classes.",
                  "Pie and line charts with matplotlib.",
                  "Optional password protection or file encryption.",
                  "Multiple currencies and PDF export of monthly reports."])
    s += section("14", "References", newPage=False)
    s += bullets(["Python Software Foundation. Python 3 documentation: decimal, json, csv, datetime, logging, unittest. https://docs.python.org/3/",
                  "PEP 8, Style Guide for Python Code. https://peps.python.org/pep-0008/",
                  "PEP 634, Structural Pattern Matching. https://peps.python.org/pep-0634/",
                  "OWASP. CSV Injection. https://owasp.org/www-community/attacks/CSV_Injection",
                  "VITyarthi. Build Your Own Project: General Project Instructions and Submission Guidelines."])

    doc.multiBuild(s)
    print(f"Report saved as {OUTPUT}")


buildReport()
