#!/usr/bin/env python3
"""Extract table of contents (chapter + section headings) from compiled LaTeX PDF."""

import os
import re
import subprocess
import sys


def extract_page_number(lines):
    for i in range(len(lines) - 1, max(len(lines) - 6, -1), -1):
        m = re.search(r"ДП\.АС64\.\d{6}-\d{2}\s+\d{2}\s+\d{2}\s+(\d+)\s*$", lines[i])
        if m:
            return int(m.group(1))
    for i in range(len(lines) - 1, max(len(lines) - 8, -1), -1):
        if re.match(r"^\s*\d+\s*$", lines[i]):
            return int(lines[i].strip())
    return None


def is_chapter_heading(line):
    stripped = line.strip()
    if not stripped:
        return False
    if any(token in stripped for token in ("Изм.", "Лист", "ДП.", "Подп.", "Дата")):
        return False
    if any(ch in stripped for ch in "[]()="):
        return False
    if re.match(r"^(?:\d+\.?\s+)?[А-ЯA-Z]{2,}", stripped):
        remaining = re.sub(r"^\d+\.?\s*", "", stripped)
        if any(c.islower() for c in remaining):
            return False
        if len(remaining) < 5:
            return False
        return True
    return False


def is_section_heading(line):
    stripped = line.strip()
    return bool(re.match(r"^\s*\d+\.\d+\s+\S", stripped))


def is_title_continuation(line):
    stripped = line.strip()
    return bool(re.match(r"^[а-я][а-яё\s\-—–,\d]+$", stripped)) and len(stripped) < 60


def main():
    # ==================== НАСТРОЙКИ ПУТЕЙ ====================
    # Папка, где лежит ваш PDF-файл
    TARGET_DIR = "/mnt/UbuntuHost/vlad/IdeaProjects/DiplomPasterisator/diplom"

    # Имя входного PDF-файла
    INPUT_PDF = "main.pdf"

    # Имя файла, в который запишется оглавление LaTeX (сохранится в TARGET_DIR)
    OUTPUT_FILE = "/mnt/UbuntuHost/vlad/IdeaProjects/DiplomPasterisator/summary/toc_generated.tex"
    # =========================================================

    # Собираем полный абсолютный путь к PDF
    pdf_path = os.path.join(TARGET_DIR, INPUT_PDF)

    # Проверяем существование файла средствами Python перед запуском
    if not os.path.exists(pdf_path):
        print(f"Ошибка: PDF-файл не найден по пути: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    # Вызов pdftotext. Параметр cwd принудительно запускает утилиту внутри нужной папки.
    result = subprocess.run(
        ["pdftotext", "-layout", pdf_path, "-"],
        capture_output=True,
        text=True,
        cwd=TARGET_DIR,
    )
    if result.returncode != 0:
        print(f"Error running pdftotext: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    pages = result.stdout.split("\f")
    headings = []

    for idx, page in enumerate(pages):
        lines = page.split("\n")
        if not lines or all(not l.strip() for l in lines):
            continue

        page_num = extract_page_number(lines)
        if page_num is None:
            page_num = idx + 5

        chapter = None
        for i, line in enumerate(lines[:10]):
            if is_chapter_heading(line):
                chapter = line.strip()
                break

        if chapter:
            if re.match(r"^\d+\.?\s", chapter):
                chapter = re.sub(r"^(\d+)\.?\s", r"\1 ", chapter, count=1)

            headings.append(("chapter", chapter, page_num))

        for i, line in enumerate(lines):
            if is_section_heading(line):
                title = line.strip()

                next_line = lines[i + 1] if i + 1 < len(lines) else ""
                if is_title_continuation(next_line):
                    if title.endswith("-"):
                        title = title[:-1]
                    title += next_line.strip()

                headings.append(("section", title, page_num))

    # Формируем строки для записи в итоговый документ
    output_lines = []
    for htype, title, page in headings:
        if htype == "chapter":
            output_lines.append(f"\\par {{\\bfseries {title} \\dotfill {page}}}")
        else:
            output_lines.append(f"\\par {title} \\dotfill {page}")

    # Принудительно добавляем Приложение А в самый конец списка (без номера страницы)
    output_lines.append(r"\par {\bfseries ПРИЛОЖЕНИЕ А: ТЕКСТ ПРОГРАММЫ}")

    output_text = "\n".join(output_lines) + "\n"

    # Определяем полный путь для сохранения .tex файла
    if not os.path.isabs(OUTPUT_FILE):
        out_path = os.path.join(TARGET_DIR, OUTPUT_FILE)
    else:
        out_path = OUTPUT_FILE

    # Проверяем существование папки script, если путь относительный
    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    # Записываем результат в файл
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(output_text)
        print(f"Готово! Оглавление успешно записано в файл:\n{out_path}")
    except IOError as e:
        print(f"Ошибка при записи файла {out_path}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
