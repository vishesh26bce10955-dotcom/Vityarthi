import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Ellipse, FancyBboxPatch, Polygon, Rectangle

for fontFile in ("segoeui.ttf", "segoeuib.ttf"):
    font_manager.fontManager.addfont(f"C:/Windows/Fonts/{fontFile}")
plt.rcParams["font.family"] = "Segoe UI"

IMAGE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "images")
BLUE = "#E2E8F0"
GREEN = "#CCFBF1"
YELLOW = "#FEF3C7"
GREY = "#F1F5F9"
EDGE = "#0F172A"


# 1. Create a blank drawing canvas measured in simple units
def newCanvas(width: int, height: int, title: str):
    fig, ax = plt.subplots(figsize=(width / 10, height / 10))
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


# 2. Draw a rounded box with centred text
def box(ax, x: float, y: float, w: float, h: float, text: str, fc: str = BLUE, fs: int = 9, bold: bool = False) -> None:
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.4,rounding_size=1.5", fc=fc, ec=EDGE, lw=1.0))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, fontweight="bold" if bold else "normal")


# 3. Draw an arrow with an optional label
def arrow(ax, x1: float, y1: float, x2: float, y2: float, text: str = "", dashed: bool = False, fs: int = 8) -> None:
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", lw=1.1, color="#333333", linestyle="--" if dashed else "-"))
    if text:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 1.2, text, ha="center", va="bottom", fontsize=fs, color="#333333",
                bbox=dict(fc="white", ec="none", pad=0.6))


# 4. Save the figure into docs/images
def saveImage(fig, fileName: str) -> None:
    os.makedirs(IMAGE_FOLDER, exist_ok=True)
    fig.savefig(os.path.join(IMAGE_FOLDER, fileName), dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# 5. System architecture diagram
def architectureDiagram() -> None:
    fig, ax = newCanvas(130, 96, "System Architecture (Layered)")
    layers = [(82, "Presentation layer", "#F8FAFC"), (58, "Business logic layer", "#F0FDFA"),
              (34, "Data layer", "#FFFBEB"), (12, "Cross-cutting", "#F1F5F9")]
    for y, name, colour in layers:
        ax.add_patch(Rectangle((3, y - 9), 124, 18, fc=colour, ec="#999999", lw=0.8))
        ax.text(5, y + 6.5, name, fontsize=9, fontweight="bold", color="#555555")
    box(ax, 30, 81, 34, 9, "Main.py\n(entry point)", BLUE, 9, True)
    box(ax, 85, 81, 50, 9, "Menu.py\n(CLI menus, input and output)", BLUE, 9, True)
    box(ax, 22, 57, 30, 9, "Expense_Manager\nCRUD + search", GREEN, 9, True)
    box(ax, 57, 57, 30, 9, "Budget_Manager\nlimits + alerts", GREEN, 9, True)
    box(ax, 91, 57, 26, 9, "Reports\nsummaries + charts", GREEN, 9, True)
    box(ax, 116, 57, 20, 9, "Csv_Transfer\nimport/export", GREEN, 8, True)
    box(ax, 22, 33, 30, 9, "Expense_Model\nExpense class", YELLOW, 9, True)
    box(ax, 57, 33, 30, 9, "Storage\nJsonStorage", YELLOW, 9, True)
    box(ax, 100, 33, 34, 9, "data/expenses.json\n(atomic writes)", "#ffffff", 9)
    box(ax, 30, 11, 34, 9, "Validators\nchecks all user input", GREY, 9, True)
    box(ax, 75, 11, 30, 9, "Logger", GREY, 9, True)
    box(ax, 110, 11, 28, 9, "logs/expense_tracker.log", "#ffffff", 8)
    arrow(ax, 45, 81, 60, 81, "")
    arrow(ax, 75, 76, 30, 62, "")
    arrow(ax, 82, 76, 57, 62, "")
    arrow(ax, 88, 76, 91, 62, "")
    arrow(ax, 100, 76, 114, 62, "")
    arrow(ax, 22, 52, 22, 38, "")
    arrow(ax, 22, 52, 55, 38, "")
    arrow(ax, 57, 52, 57, 38, "")
    arrow(ax, 72, 33, 83, 33, "read/write")
    arrow(ax, 30, 16.5, 22, 52, "", True)
    arrow(ax, 75, 16.5, 57, 28, "", True)
    saveImage(fig, "architecture.png")


# 6. Use case diagram
def useCaseDiagram() -> None:
    fig, ax = newCanvas(130, 104, "Use Case Diagram")
    ax.add_patch(Rectangle((40, 3), 88, 92, fc="#fbfbfb", ec="#666666", lw=1))
    ax.text(84, 91, "Expense Tracker System", ha="center", fontsize=10, fontweight="bold")
    ax.add_patch(plt.Circle((14, 60), 3, fc="white", ec="black"))
    ax.plot([14, 14], [57, 46], "k")
    ax.plot([7, 21], [53, 53], "k")
    ax.plot([14, 8], [46, 37], "k")
    ax.plot([14, 20], [46, 37], "k")
    ax.text(14, 32, "User", ha="center", fontsize=10, fontweight="bold")
    cases = [(84, 82, "Add expense"), (84, 72, "View / search expenses"), (84, 62, "Update expense"),
             (84, 52, "Delete expense"), (84, 42, "Set / remove budget"), (84, 32, "View budget status"),
             (84, 22, "View reports"), (84, 12, "Export CSV"), (112, 22, "Import CSV")]
    for x, y, text in cases:
        ax.add_patch(Ellipse((x, y), 34 if len(text) > 14 else 28, 7.5, fc=BLUE, ec=EDGE))
        ax.text(x, y, text, ha="center", va="center", fontsize=8.5)
        ax.plot([17, x - (17 if len(text) > 14 else 14)], [50, y], color="#555555", lw=0.8)
    ax.add_patch(Ellipse((112, 50), 26, 8, fc=YELLOW, ec=EDGE))
    ax.text(112, 50, "Validate input", ha="center", va="center", fontsize=8.5)
    arrow(ax, 98, 80, 110, 54, "", True)
    arrow(ax, 98, 62, 106, 53.5, "", True)
    arrow(ax, 112, 26, 112, 46, "", True)
    ax.text(115, 37, "<<include>>", fontsize=7.5, rotation=90, va="center")
    saveImage(fig, "use_case.png")


# 7. Workflow (flowchart) diagram
def workflowDiagram() -> None:
    fig, ax = newCanvas(130, 150, "Process Flow: User Interaction")
    box(ax, 40, 142, 30, 7, "Start", GREEN, 9, True)
    box(ax, 40, 129, 44, 8, "Load data file\n(recover if corrupt)", BLUE)
    box(ax, 40, 116, 44, 8, "Show budget alerts\nfor this month", BLUE)
    box(ax, 40, 103, 40, 8, "Show main menu", BLUE, 9, True)
    ax.add_patch(Polygon([[40, 94], [58, 86], [40, 78], [22, 86]], fc=YELLOW, ec=EDGE))
    ax.text(40, 86, "Choice?", ha="center", va="center", fontsize=9)
    box(ax, 105, 103, 34, 8, "Expenses menu", BLUE)
    box(ax, 105, 92, 34, 8, "Budgets menu", BLUE)
    box(ax, 105, 81, 34, 8, "Reports menu", BLUE)
    box(ax, 105, 70, 34, 8, "Import / Export menu", BLUE)
    box(ax, 40, 66, 34, 8, "Exit: say goodbye", GREEN, 9, True)
    ax.add_patch(Polygon([[105, 60], [123, 53], [105, 46], [87, 53]], fc=YELLOW, ec=EDGE))
    ax.text(105, 53, "Input\nvalid?", ha="center", va="center", fontsize=9)
    box(ax, 105, 36, 40, 9, "Run operation, save file\n(atomic write), write log", GREEN)
    box(ax, 55, 44, 34, 9, "Show error message\nand write warning log", "#FEE2E2")
    box(ax, 80, 22, 60, 8, "Show result message, return to main menu", BLUE)
    box(ax, 40, 142, 30, 7, "Start", GREEN, 9, True)
    arrow(ax, 40, 138, 40, 133)
    arrow(ax, 40, 125, 40, 120)
    arrow(ax, 40, 112, 40, 107)
    arrow(ax, 40, 99, 40, 94)
    arrow(ax, 58, 86, 88, 103, "1")
    arrow(ax, 58, 86, 88, 92, "2")
    arrow(ax, 58, 86, 88, 81, "3")
    arrow(ax, 58, 86, 88, 70, "4")
    arrow(ax, 40, 78, 40, 70, "5")
    arrow(ax, 105, 66, 105, 60)
    arrow(ax, 87, 53, 72, 47, "no")
    arrow(ax, 105, 46, 105, 40.5, "yes")
    arrow(ax, 105, 31.5, 95, 26)
    arrow(ax, 55, 39.5, 70, 26)
    ax.plot([10, 10], [22, 103], color="#333333", lw=1.1)
    ax.plot([10, 20], [22, 22], color="#333333", lw=1.1)
    ax.annotate("", xy=(20, 103), xytext=(10, 103), arrowprops=dict(arrowstyle="->", lw=1.1))
    ax.set_ylim(15, 148)
    saveImage(fig, "workflow.png")


# 8. Sequence diagram for adding an expense
def sequenceDiagram() -> None:
    fig, ax = newCanvas(140, 120, "Sequence Diagram: Add Expense")
    names = ["User", "Menu", "ExpenseManager", "Validators", "JsonStorage", "Logger"]
    xs = [12, 34, 58, 82, 104, 128]
    for x, name in zip(xs, names):
        box(ax, x, 112, 18, 6, name, BLUE, 8.5, True)
        ax.plot([x, x], [108, 6], color="#777777", lw=0.9, linestyle="--")
    steps = [(0, 1, "choose 'Add expense'"), (0, 1, "amount, category, description, date"),
             (1, 2, "addExpense(amount, category, description, date)"), (2, 3, "validateAmount / Category / Description / Date"),
             (3, 2, "clean values (or ValueError)"), (2, 4, "append record, nextId += 1, save()"),
             (4, 4, "write temp file, os.replace()"), (2, 5, "info('Added expense ...')"),
             (2, 1, "'Expense added with ID n.'"), (1, 0, "print(message)")]
    y = 100
    for a, b, text in steps:
        if a == b:
            ax.annotate("", xy=(xs[a] + 0.5, y - 4), xytext=(xs[a] + 0.5, y), arrowprops=dict(arrowstyle="->", lw=1.1, connectionstyle="arc3,rad=-1.5"))
            ax.text(xs[a] + 4, y - 2, text, fontsize=7.5, va="center")
        else:
            arrow(ax, xs[a], y, xs[b], y, "", dashed=b < a)
            ax.text((xs[a] + xs[b]) / 2, y + 1, text, ha="center", va="bottom", fontsize=7.5)
        y -= 8.5
    ax.add_patch(Rectangle((2, 4), 136, 12, fc="#FEE2E2", ec="#aa4444", lw=0.8, alpha=0.6))
    ax.text(70, 10, "If validation fails: ValueError goes back to Menu, which prints 'An error occurred: ...' and shows the main menu again.",
            ha="center", va="center", fontsize=7.5)
    saveImage(fig, "sequence.png")


# 9. Draw a UML class box with attributes and methods
def classBox(ax, x: float, y: float, w: float, title: str, attributes: list, methods: list, fc: str = BLUE) -> None:
    lineHeight = 3.1
    h = 6 + lineHeight * (len(attributes) + len(methods)) + 3
    top = y + h / 2
    ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h, fc="white", ec=EDGE, lw=1.3))
    ax.add_patch(Rectangle((x - w / 2, top - 6), w, 6, fc=fc, ec=EDGE, lw=1.3))
    ax.text(x, top - 3, title, ha="center", va="center", fontsize=8.5, fontweight="bold")
    cursor = top - 6 - 2
    for line in attributes:
        ax.text(x - w / 2 + 1.2, cursor, line, va="center", fontsize=7)
        cursor -= lineHeight
    ax.plot([x - w / 2, x + w / 2], [cursor + 1.3, cursor + 1.3], color=EDGE, lw=1)
    cursor -= 0.8
    for line in methods:
        ax.text(x - w / 2 + 1.2, cursor, line, va="center", fontsize=7)
        cursor -= lineHeight


# 10. Class diagram
def classDiagram() -> None:
    fig, ax = newCanvas(150, 120, "Class / Component Diagram")
    classBox(ax, 26, 92, 44, "Expense", ["+ expenseId: int", "+ amount: Decimal", "+ category: str", "+ description: str", "+ date: str"],
             ["+ toDict(): dict", "+ fromDict(data): Expense"], YELLOW)
    classBox(ax, 26, 50, 44, "JsonStorage", ["+ fileName: str", "+ data: dict", "+ logger: Logger"],
             ["+ load(): dict", "+ save(): None", "+ emptyData(): dict"], YELLOW)
    classBox(ax, 78, 90, 48, "ExpenseManager", ["+ storage: JsonStorage"],
             ["+ addExpense(...): str", "+ listExpenses(): list", "+ getExpense(id): Expense", "+ updateExpense(...): str",
              "+ deleteExpense(id): str", "+ searchExpenses(...): list", "+ listCategories(): list"], GREEN)
    classBox(ax, 78, 44, 48, "BudgetManager", ["+ storage: JsonStorage", "+ expenseManager: ExpenseManager"],
             ["+ setBudget(category, amount): str", "+ removeBudget(category): str", "+ budgetStatus(month): list", "+ budgetAlerts(month): list"], GREEN)
    classBox(ax, 128, 100, 40, "<<module>> Reports", [], ["+ totalAmount()", "+ categoryTotals()", "+ categoryChart()", "+ monthlySummary()",
                                                          "+ topExpenses()", "+ monthlyTrend()"], "#E0E7FF")
    classBox(ax, 128, 66, 40, "<<module>> Csv_Transfer", [], ["+ exportCsv()", "+ importCsv()", "+ makeSafeCell()", "+ undoSafeCell()"], "#E0E7FF")
    classBox(ax, 128, 34, 40, "<<module>> Validators", [], ["+ validateAmount()", "+ validateDate()", "+ validateMonth()", "+ validateCategory()",
                                                             "+ validateDescription()", "+ validateId()"], "#E0E7FF")
    classBox(ax, 26, 14, 44, "<<module>> Menu", [], ["+ mainMenu(): str", "+ expenseMenu() / budgetMenu()", "+ reportMenu() / transferMenu()"], "#E0E7FF")
    arrow(ax, 58, 73, 46, 60, "uses")
    arrow(ax, 54, 46, 48, 46, "uses")
    arrow(ax, 78, 58, 78, 73, "uses")
    arrow(ax, 54, 92, 48, 92, "creates", True)
    arrow(ax, 108, 68, 102, 80, "uses", True)
    arrow(ax, 102, 76, 108, 44, "uses", True)
    arrow(ax, 26, 24, 26, 36, "creates", True)
    ax.text(78, 10, "Menu calls the managers, Reports and Csv_Transfer.\nReports works on lists of Expense objects.", ha="center", fontsize=8)
    saveImage(fig, "class_diagram.png")


# 11. Draw an ER entity table
def entityTable(ax, x: float, y: float, w: float, title: str, rows: list) -> None:
    lineHeight = 4.5
    h = 7 + lineHeight * len(rows)
    ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h, fc="white", ec=EDGE, lw=1.3))
    ax.add_patch(Rectangle((x - w / 2, y + h / 2 - 7), w, 7, fc=BLUE, ec=EDGE, lw=1.3))
    ax.text(x, y + h / 2 - 3.5, title, ha="center", va="center", fontsize=10, fontweight="bold")
    cursor = y + h / 2 - 7 - 2.6
    for key, name, kind in rows:
        ax.text(x - w / 2 + 1.5, cursor, key, fontsize=8, fontweight="bold", color="#aa2222", va="center")
        ax.text(x - w / 2 + 9, cursor, name, fontsize=8.5, va="center")
        ax.text(x + w / 2 - 1.5, cursor, kind, fontsize=8, ha="right", va="center", color="#555555")
        cursor -= lineHeight


# 12. ER diagram and JSON schema
def erDiagram() -> None:
    fig, ax = newCanvas(140, 70, "ER Diagram (JSON storage schema)")
    entityTable(ax, 28, 35, 46, "BUDGET", [("PK", "category", "string"), ("", "monthlyLimit", "decimal string")])
    entityTable(ax, 108, 38, 50, "EXPENSE", [("PK", "id", "integer"), ("FK", "category", "string"), ("", "amount", "decimal string"),
                                            ("", "description", "string"), ("", "date", "YYYY-MM-DD")])
    ax.plot([51, 83], [35, 35], color="#333333", lw=1.3)
    ax.text(54, 37, "1", fontsize=10, fontweight="bold")
    ax.text(76, 37, "0..*", fontsize=10, fontweight="bold")
    ax.text(67, 31, "category is\nspent against", ha="center", fontsize=8)
    entityTable(ax, 60, 8, 40, "META", [("", "nextId", "integer")])
    saveImage(fig, "er_diagram.png")


# 13. Build every diagram
def buildAll() -> None:
    architectureDiagram()
    useCaseDiagram()
    workflowDiagram()
    sequenceDiagram()
    classDiagram()
    erDiagram()
    print(f"Diagrams saved in {os.path.abspath(IMAGE_FOLDER)}")


buildAll()
