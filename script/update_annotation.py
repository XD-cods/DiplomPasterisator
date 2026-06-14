#!/usr/bin/env python3
"""Автоматический подсчёт и обновление метаданных аннотации."""

import os
import re
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIPLOM_PDF = os.path.join(BASE_DIR, "..", "diplom", "main.pdf")
ANNOTATION_TEX = os.path.join(BASE_DIR, "..", "annotation", "annotation.tex")
ANNOTATION_DIR = os.path.dirname(ANNOTATION_TEX)


def extract_text(pdf_path):
    result = subprocess.run(
        ["pdftotext", "-layout", pdf_path, "-"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"Ошибка pdftotext: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout


def get_last_page_number(text):
    pages = text.split("\f")
    for page in reversed(pages):
        for line in reversed(page.split("\n")):
            m = re.search(r"ДП\.АС64\.\d{6}-\d{2}\s+\d{2}\s+\d{2}\s+(\d+)\s*$", line)
            if m:
                return int(m.group(1))
    return None


def count_unique(text, pattern):
    numbers = set()
    for m in re.finditer(pattern, text):
        numbers.add(m.group(1))
    return len(numbers)


def count_sources(text):
    idx = text.rfind("СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ")
    if idx < 0:
        return 0
    section = text[idx:]
    count = 0
    for line in section.split("\n"):
        if re.match(r"^\s*\d+\.\s+[А-ЯA-Z]", line.strip()):
            count += 1
    return count


def update_annotation_tex(total_pages, total_plus_4, figures, tables, sources):
    with open(ANNOTATION_TEX, "r", encoding="utf-8") as f:
        content = f.read()

    new_line = (
        f"\\par \\redline {total_pages} с./ {total_plus_4} с.,"
        f"  {figures} рис.,  {tables} табл.,"
        f" {sources} исп. ист., 1 прил., 5 граф. матер."
    )

    pattern = (
        r"\\par\s*\\redline\s*\d+\s*с\./\s*\d+\s*с\.,\s*\d+\s*рис\.,"
        r"\s*\d+\s*табл\.,\s*\d+\s*исп\.\s*ист\.,\s*\d+\s*прил\.,"
        r"\s*\d+\s*граф\.\s*матер\."
    )
    content = re.sub(pattern, lambda _: new_line, content)

    with open(ANNOTATION_TEX, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Аннотация обновлена: {new_line}")


def compile_annotation():
    result = subprocess.run(
        ["latexmk", "-xelatex", "-silent", "-interaction=nonstopmode", "annotation.tex"],
        cwd=ANNOTATION_DIR,
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"Ошибка компиляции annotation: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    print("annotation/main.pdf перекомпилирован")


def main():
    if not os.path.exists(DIPLOM_PDF):
        print(f"Ошибка: {DIPLOM_PDF} не найден", file=sys.stderr)
        sys.exit(1)

    text = extract_text(DIPLOM_PDF)

    total_pages = get_last_page_number(text)
    if total_pages is None:
        print("Ошибка: не удалось определить номер последней страницы", file=sys.stderr)
        sys.exit(1)

    total_plus_4 = total_pages + 4

    figures = count_unique(text, r"Рисунок\s+(\d+(?:\.\d+)?)\s*[–-]")
    tables = count_unique(text, r"Таблица\s+(\d+(?:\.\d+)?)\s*[–-]")
    sources = count_sources(text)

    print(f"Страниц: {total_pages} / {total_plus_4} | Рис.: {figures} | Табл.: {tables} | Ист.: {sources} | Прил.: 1 | Граф. мат.: 5")

    update_annotation_tex(total_pages, total_plus_4, figures, tables, sources)
    compile_annotation()


if __name__ == "__main__":
    main()