import builtins
import contextlib
import io
import os
import re
import shutil
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
IMAGE_FOLDER = os.path.join(ROOT, "docs", "images")
FONT_FILE = "C:/Windows/Fonts/consola.ttf"
FONT_SIZE = 16

os.chdir(ROOT)
sys.path.insert(0, ROOT)

from tracker import Menu


# 1. Run the real program with scripted answers and record what a user would see
def runScene(answers: list) -> str:
    remaining = list(answers)

    def fakeInput(prompt: str = "") -> str:
        if not remaining:
            raise EOFError
        answer = remaining.pop(0)
        print(f"{prompt}{answer}")
        return answer

    buffer = io.StringIO()
    originalInput = builtins.input
    builtins.input = fakeInput
    try:
        with contextlib.redirect_stdout(buffer):
            print(Menu.mainMenu())
    finally:
        builtins.input = originalInput
    return buffer.getvalue().strip("\n")


# 1b. Show each menu only once so the screenshots stay short and readable
def compactText(text: str) -> str:
    seenMenus = set()
    result = []
    menu = []
    for line in text.split("\n"):
        if line.startswith("===== Expense Tracker"):
            if "main" in seenMenus:
                if result and result[-1] == "":
                    result.pop()
                continue
            seenMenus.add("main")
        if re.match(r"^\d\. ", line):
            menu.append(line)
            continue
        if menu:
            key = tuple(menu)
            if key not in seenMenus:
                seenMenus.add(key)
                result.extend(menu)
            menu = []
        result.append(line)
    return "\n".join(result)


# 2. Draw text as a dark terminal-style screenshot
def renderImage(text: str, fileName: str) -> None:
    font = ImageFont.truetype(FONT_FILE, FONT_SIZE)
    lines = compactText(text).split("\n")
    charWidth = font.getlength("M")
    lineHeight = FONT_SIZE + 5
    width = int(max(len(line) for line in lines) * charWidth) + 40
    height = lineHeight * len(lines) + 60
    image = Image.new("RGB", (width, height), (15, 23, 42))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, 28), fill=(30, 41, 59))
    for i, colour in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        draw.ellipse((12 + i * 20, 9, 22 + i * 20, 19), fill=colour)
    draw.text((width // 2 - 60, 6), "Expense Tracker", font=ImageFont.truetype(FONT_FILE, 13), fill=(180, 185, 195))
    for i, line in enumerate(lines):
        colour = (240, 200, 110) if line.startswith(("WARNING", "OVER BUDGET", "An error occurred")) else (215, 220, 228)
        draw.text((20, 42 + i * lineHeight), line, font=font, fill=colour)
    image.save(os.path.join(IMAGE_FOLDER, fileName))


# 3. Build every screenshot from scripted sessions that share one data file
def buildAll() -> None:
    os.makedirs(IMAGE_FOLDER, exist_ok=True)
    folder = tempfile.mkdtemp()
    Menu.DATA_FILE = os.path.join(folder, "expenses.json")
    try:
        renderImage(runScene(["4", "2", "data/sample_expenses.csv", "1", "2", "5"]), "shot_import.png")
        renderImage(runScene(["1", "1", "abc", "food", "Coffee", "", "1", "1", "45.50", "food", "Coffee with friends", "",
                              "1", "5", "coffee", "", "", "", "", "", "5"]), "shot_add_search.png")
        renderImage(runScene(["1", "3", "14", "52", "", "", "", "1", "4", "14", "y", "5"]), "shot_update_delete.png")
        setup = runScene(["2", "1", "rent", "6500", "2", "1", "food", "1000", "2", "1", "entertainment", "1500", "2", "1", "books", "1000",
                          "2", "3", "2026-09", "5"])
        restart = runScene(["5"])
        renderImage(f"{setup}\n\n--- program restarted ---\n\n{restart}", "shot_budgets.png")
        renderImage(runScene(["3", "1", "2026-09", "3", "2", "5"]), "shot_reports_summary.png")
        renderImage(runScene(["3", "3", "3", "4", "5"]), "shot_reports_top_trend.png")
        renderImage(runScene(["4", "1", "export_demo.csv", "5"]), "shot_export.png")
    finally:
        shutil.rmtree(folder, ignore_errors=True)
        for leftover in ("export_demo.csv", "logs"):
            if os.path.isdir(leftover):
                shutil.rmtree(leftover, ignore_errors=True)
            elif os.path.exists(leftover):
                os.remove(leftover)
    print(f"Screenshots saved in {IMAGE_FOLDER}")


buildAll()
