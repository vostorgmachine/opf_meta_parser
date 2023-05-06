from pathlib import Path
import os
import subprocess
import markdown
import re


def meta_parser(md_directory):
    # Чтобы вывести переменную из функции, применяется "глобальная переменная":
    global title
    global seriya
    global seriya_num
    global authors
    global tags

    for file in md_directory:
        file = open(file, "r", encoding="utf-8")
        for md_string in file:
            if "##" in md_string:
                title = md_string
                title = title.replace("## ", "").replace("\n", "")
            else:
                title = "no_title in " + str(file)

            if "Серия:" in md_string:
                seriya = md_string
                seriya = seriya.replace("Серия: ", "").replace("№", "No: ")
                # Данная часть кода работает засчёт модуля re
                # и на выходе даёт переменную nums, которая содержит номер серии,
                # выраженный отдельным числом:
                seriya_num = seriya
                nums = re.findall(r"\d+", seriya_num)
                nums = [int(i) for i in nums]
                seriya_num = nums
            else:
                seriya = "no_seriya in " + str(file)
                seriya_num = "no_seriya_num in " + str(file)

            if "Автор(ы):" in md_string:
                authors = md_string
                authors = authors.replace("Автор(ы): ", "")
            else:
                authors = "no_authors in " + str(file)

            # В данном случае происходит забор строки, далее она "очищается" от
            # ненужных символов, после чего конвертируется в список, который, в
            # свою очередь переворачивается задом на перёд. В конце-концов
            # создаётся строка, разделителем в которой является символ "-".
            if "Дата публикации статьи:" in md_string:
                date = md_string
                date = (
                    date.replace("Дата публикации статьи: ", "")
                    .replace("\n", "")
                    .replace(" ", "")
                )
                date = date.split(".")[::-1]
                date = "-".join(date)
            else:
                date = "no_date in " + str(file)

            if "Теги:" in md_string:
                tags = md_string
                tags = tags.replace("Теги: ", "")
            else:
                tags = "no_tags in " + str(file)

        file.seek(0)  # откат каретки


meta_parser()

print(title)
print(seriya)
print(seriya_num)
print(authors)
print(tags)

# Скорее всего на данный момент самым верным будет сделать один большой цикл,
# который перебирает все файлы из специально заготовленного списка:

# Анализ файлов в папке ---> создание списка ---> прогон по функции --->
# генерация опф ---> след. повторение
