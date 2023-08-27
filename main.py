#!/bin/python

import glob
from Markdown2docx import Markdown2docx
from pathlib import Path
import os
import subprocess
import markdown
import re

md_directory = glob.glob("*.md")

n = 0

while n < len(md_directory):

    md_file = open(md_directory[n], "r", encoding="utf-8")

    for md_string in md_file:

        if "##" in md_string:
            title = md_string
            title = title.strip("## ").strip("\n")
            print("title:")
            print(title)
            md_file.seek(0)
            break

    for md_string in md_file:

        if "Серия:" in md_string:
            seriya = md_string
            seriya = seriya.strip("Серия: ").replace("№", "No: ")

            # Данная часть кода работает засчёт модуля re
            # и на выходе даёт переменную nums, которая содержит номер серии,
            # выраженный отдельным числом:
            seriya_num = seriya
            nums = re.findall(r"\d+", seriya_num)
            nums = [int(i) for i in nums]
            seriya_num = nums
            md_file.seek(0)

            print("seriya:")
            print(seriya)
            md_file.seek(0)
            break

    for md_string in md_file:

        if "Автор(ы):" in md_string:
            authors = md_string.replace("Автор(ы): ", "")
            print("authors:")
            print(authors)
            md_file.seek(0)
            break

        # else:
        #     authors = "Неизвестный"
        #     md_file.seek(0)
        #     break

        # В данном случае происходит забор строки, далее она "очищается" от
        # ненужных символов, после чего конвертируется в список, который, в
        # свою очередь переворачивается задом на перёд. В конце-концов
        # создаётся строка, разделителем в которой является символ "-".

    for md_string in md_file:

        if "Дата публикации статьи:" in md_string:
            date = md_string
            date = (
                date.strip("Дата публикации статьи: ")
                .strip("\n")
                .strip(" ")
            )
            date = date.split(".")[::-1]
            date = "-".join(date)
            md_file.seek(0)
            break

    for md_string in md_file:
        if "Теги: " in md_string:
            tags = md_string
            tags = tags.strip("Теги: ")
            md_file.seek(0)
            break

    # --------------------------------------------------
    # maker
    # --------------------------------------------------

    # В данном случае задействован метод split(), позволяющий трансформировать
    # строку в список. В качестве "разделителя" указан "&":

    authors_list = authors.split("&")

    second_authors_list = []
    for i in authors_list:
        i = i.strip()
        second_authors_list.append(i)
    authors_list = second_authors_list

    # Цикл для дробления элементов списка на отдельные слова (в данном случае имена
    # и фамилии а так же их "переворачивание([::-1])".

    authors_reversed = []
    for each_author in authors_list:
        splitted_author = each_author.split()
        reversed_author = splitted_author[-1] + ", " + splitted_author[0]
        authors_reversed.append(reversed_author)

    opf_file_name = md_file.name.replace("md/", "").replace(".md", ".opf")

    opf_file = open(("./" + opf_file_name), "w+")
    opf_head = open("/home/vostorg/sandbox/python/parser/head.opf", "r")

    # Добавление "шапки"
    opf_file.write(opf_head.read())
    opf_head.close()

    opf_file.write("<dc:title>" + title + "</dc:title>")
    opf_file.write("\n")
    opf_file.write("\n")
    # opf_file.close()

    # Данный цикл позволяет забрать список авторов и изменить разделитель его
    # элементов на необходимый : (' &amp; '.join(authors_list)) - &amp в данном
    # случае как раз и является указываемым делителем.

    i = 0

    if authors != "":

        while i < len(authors_list):
            opf_file.write(
                '<dc:creator opf:file-as="'
                + (" &amp; ".join(authors_reversed))
                + '" opf:role="aut">'
                + authors_list[i]
                + "</dc:creator>\n"
            )
            i = i + 1

    contribution = open("/home/vostorg/sandbox/python/parser/contribution.opf", "r")
    opf_file.write(contribution.read())
    contribution.close()

    opf_file.write("<dc:date>" + date + "T00:00:00+00:00</dc:date>\n")
    opf_file.write("\n")

    with open(md_file.name, "r") as f:
        markdown_file = f.read()

    html_file = markdown.markdown(markdown_file)

    opf_file.write("<dc:description>\n" + html_file + "\n</dc:description>\n")
    opf_file.write("\n")

    # Добавление тегов:
    tags_list = tags.split(", ")
    for i in tags_list:
        i = i.strip("\n")
        opf_file.write("<dc:subject>" + i + "</dc:subject>\n")

    opf_file.write("\n")

    # А вот из этого ужаса нужно однозначно делать функцию.

    if authors == "Неизвестный":
        opf_file.write(
            ' <meta name="calibre:author_link_map"\
    content="{&quot;'
            + "Неизвестный"
            + '&quot;: &quot;&quot;}"/> '
        )

    else:
        if authors != "":

            if len(authors_list) == 1 and authors != "Неизвестный" :
                opf_file.write(
                    ' <meta name="calibre:author_link_map"\
            content="{&quot;'
                    + authors_list[0]
                    + '&quot;: &quot;&quot;}"/> '
                )

            if len(authors_list) == 2:
                opf_file.write(
                    '<meta name="calibre:author_link_map" content=\
            "{&quot;'
                    + authors_list[0]
                    + "&quot;: &quot;&quot;, \
            &quot;"
                    + authors_list[1]
                    + '&quot;: &quot;&quot;}"/>'
                )

            # Добавление author link. Обязательно переделать на что-то более пристойное!
            if len(authors_list) == 3:
                opf_file.write(
                    ' <meta name="calibre:author_link_map" content="{&quot;'
                    + authors_list[0]
                    + "&quot;: &quot;&quot;, &quot;"
                    + authors_list[1]
                    + "&quot;: &quot;&quot;, &quot;"
                    + authors_list[2]
                    + ' &quot;: &quot;&quot;}"/>\n'
                )

            if len(authors_list) == 4:
                opf_file.write(
                    ' <meta name="calibre:author_link_map" content="{&quot;'
                    + authors_list[0]
                    + "&quot;: &quot;&quot;, &quot;"
                    + authors_list[1]
                    + "&quot;: &quot;&quot;, &quot;"
                    + authors_list[2]
                    + "&quot;: &quot;&quot;, &quot;"
                    + authors_list[3]
                    + ' &quot;: &quot;&quot;}"/>\n'
                )

            opf_file.write("\n")

    if "Ведомости" in seriya:
        seriya = "Ведомости"

    if seriya[-1] == "\n":
        seriya = seriya[:-1]

    opf_file.write('<meta name="calibre:series" content="' + seriya + '"/>\n\n')

    if seriya_num != "":
        opf_file.write(
            '<meta name="calibre:series_index" content="' + str(*seriya_num) + '"/>\n\n'
        )

    # Сделать временной штамп динамичным?
    opf_file.write(
        '<meta name="calibre:timestamp"\
     content="'
        + date
        + 'T00:00:00+00:00"/>\n'
    )
    opf_file.write("\n")

    if title[-1] == "\n":
        title = title[:-1]
    opf_file.write('<meta name="calibre:title_sort" content="' + title + '"/>\n')

    # Финиш

    opf_file.write("\n\n</metadata>\n<guide/>\n</package>")

    n = n + 1

md_file.close()
opf_file.close()


# Секция, отвечающая за конвертацию .md в .docx:

directory = "./"

md_files_list = []
for file in os.listdir(directory):
    if os.path.isfile(os.path.join(directory, file)) and file.endswith(".md"):
        md_files_list.append(file)


for file in md_files_list:
    project = Markdown2docx(directory + file.strip(".md"))
    project.eat_soup()
    project.save()
