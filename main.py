# !/bin/python3

from Markdown2docx import Markdown2docx
import glob 
import markdown
import re
import os

md_files = glob.glob("*.md")

search_dict= {"title":"## ", "authors":"Автор(ы): ", "seriya":"Серия: ", \
        "publication_date":"Дата публикации статьи: ", "tags":"Теги: "}

def find(filename, search_dict): 
    """функция для поиска метаданных по словарю."""

    result = {}

    # Формирование двух списков. 
    # Один содержит ключи, другой - их значения.

    search_list_keys = []
    for i in search_dict.keys():
        search_list_keys.append(i)

    search_list_values = []
    for i in search_dict.values():
        search_list_values.append(i)

    with open(filename) as file:
        result["file_name"] = filename


        # Переписать код таким образом, чтобы поиск шёл по ограниченному
        # количеству строк (т.е только по самомоу началу файла.)
        for string in file:
            n = 0
            while n < len(search_list_keys):

                if string.startswith(search_list_values[n]):

                    result[search_list_keys[n]] =\
                    string.strip(search_dict[search_list_keys[n]]).strip("\n")
                n = n + 1

    # В случае, если "авторов" в статье не окажется, данная строка 
    # объявит автора неизвестным.

    result['authors'] = 'Неизвестный' if result.get('authors') \
            is None else result['authors']+''
    
    result['authors'] = result['authors'].split(" & ")

    file.close()
    return result

def displayer(file_list): # Функция для дебага

    n = 0
    print("--------------------------------------------------")
    print("total amount of files: ", len(file_list))
    while n < len(file_list):

        result = find(file_list[n], search_dict)
        print("--------------------------------------------------")
        for i in result:
            print(i + ": ", result[i], '\n')
        n = n + 1
        result = {}

def author_reverser(author_list): # функция обработки авторов

    reversed_author_list = []
    reversed_author_string = ''

    if "Неизвестный" not in author_list:

        for i in author_list:
            i = i.split()
            reversed_author = i[-1] + ", " + i[0]
            reversed_author_list.append(reversed_author)
            reversed_author_string = ' &amp; '.join(reversed_author_list)

    else:
        return "Неизвестный"

    return reversed_author_string

def author_link_map(author_list):

    start = '<meta name="calibre:author_link_map" content="{'
    end = '}"/>'
    middle = ''

    n = 0
    while n < len(author_list):
        middle = middle + "&quot;" + author_list[n]+' &quot;: &quot;&quot;,'
        n += 1

    final = start, middle, end
    return str(final)

def make_opf_file(result_dict):

    opf_file_name = result_dict["file_name"].replace(".md", ".opf")
    opf_file = open((opf_file_name), "w+")

    opf_head = open("/home/vostorg/sandbox/python/opf_meta_parser/head.opf", "r")
    opf_file.write(opf_head.read())

    opf_file.write("<dc:title>" + result_dict["title"] + "</dc:title>\n\n")

    n = 0

    author_list = result_dict["authors"]

    first_section = '<dc:creator opf:file-as="' + author_reverser(author_list) +  '" opf:role="aut">'

    # print(type(first_section))

    if "Неизвестный" not in author_list:

        while n < len(author_list):
            opf_file.write(first_section)
            opf_file.write(author_list[n] + "</dc:creator>\n\n")
            n = n + 1
    else:
            opf_file.write(first_section)
            # hardcode!(4r
            opf_file.write("Неизвестный")
            opf_file.write("</dc:creator>\n\n")

    opf_file.write("<dc:date>" + result_dict["publication_date"] +\
                   "T00:00:00+00:00</dc:date>\n\n")

    with open(result_dict['file_name'], "r") as f:
        markdown_file = f.read()

    html_file = markdown.markdown(markdown_file)

    opf_file.write("<dc:description>\n" + html_file + "\n</dc:description>\n")
    opf_file.write("\n")

    # Добавление тегов:
    tags_list = result_dict['tags'].split(", ")
    for i in tags_list:
        i = i.strip("\n")
        opf_file.write("<dc:subject>" + i + "</dc:subject>\n\n")

    opf_file.write("\n")

    opf_file.write(str(author_link_map(author_list)))

    if "Ведомости" in result_dict['seriya']:

        nums = re.findall(r"\d+", result_dict['seriya'])
        seriya_num = [int(i) for i in nums]

        opf_file.write('<meta name="calibre:series" content="' +\
                "Ведомости" + '"/>\n\n')

        opf_file.write('<meta name="calibre:series_index" content="' +\
                str(seriya_num) + '"/>\n\n') 
    
    else:

        opf_file.write('<meta name="calibre:series" content="' +\
                result_dict['seriya']+ '"/>\n\n')

    opf_file.write('<meta name="calibre:title_sort" content="' +
                   result_dict['title'] + '"/>\n\n')

    opf_file.write( '<meta name="calibre:timestamp"\
     content="'
        + result_dict['publication_date']
        + 'T00:00:00+00:00"/>\n\n'
    )
    opf_file.write("\n\n</metadata>\n<guide/>\n</package>")

    opf_file.close()

def create_docx():
    '''
    Генератор docx файлов, который работает засчёт Markdown2docx-библиотеки
    '''

    directory = "./"

    md_files_list = []
    for file in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, file)) and file.endswith(".md"):
            md_files_list.append(file)


    for file in md_files_list:
        project = Markdown2docx(directory + file.strip(".md"))
        project.eat_soup()
        project.save()

# main--------------------------------------------------

counter = 0
while counter < len(md_files):
    make_opf_file(find(md_files[counter], search_dict))
    counter += 1

create_docx()
