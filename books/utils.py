import json
import uuid
import xml.etree.ElementTree as ET

from pathlib import Path
from django.conf import settings


def get_books_folder():
    folder = Path(settings.MEDIA_ROOT) / 'books'
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def save_book(book, file_format):
    folder = get_books_folder()

    # Генерируем уникальное имя
    filename = f'{uuid.uuid4().hex}.{file_format}'
    filepath = folder / filename

    if file_format == 'json':

        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(
                book,
                file,
                ensure_ascii=False,
                indent=4
            )

    elif file_format == 'xml':

        root = ET.Element('book')

        for key, value in book.items():
            element = ET.SubElement(root, key)
            element.text = str(value)

        tree = ET.ElementTree(root)

        tree.write(
            filepath,
            encoding='utf-8',
            xml_declaration=True
        )

    else:
        raise ValueError('Неподдерживаемый формат файла')

    return filename

def validate_book(data):

    if not isinstance(data, dict):
        raise ValueError('Данные должны быть объектом')

    required_fields = {
        'title',
        'author',
        'year',
        'pages'
    }

    if set(data.keys()) != required_fields:
        raise ValueError('Неверная структура данных')

    if not isinstance(data['title'], str):
        raise ValueError('Название должно быть строкой')

    if not 0 < len(data['title'].strip()) <= 100:
        raise ValueError('Некорректное название книги')

    if not isinstance(data['author'], str):
        raise ValueError('Автор должен быть строкой')

    if not 0 < len(data['author'].strip()) <= 100:
        raise ValueError('Некорректное имя автора')

    from datetime import date

    for field in ('year', 'pages'):
        if type(data[field]) is not int:
            raise ValueError(f'Поле {field} должно быть целым числом')

    if not 1450 <= data['year'] <= date.today().year:
        raise ValueError('Некорректный год издания')

    if data['pages'] < 1:
        raise ValueError('Количество страниц должно быть больше нуля')

    return data


def read_book(filepath):

    if filepath.suffix.lower() == '.json':

        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)

    elif filepath.suffix.lower() == '.xml':

        tree = ET.parse(filepath)
        root = tree.getroot()

        if root.tag != 'book':
            raise ValueError('Неверный корневой элемент XML')

        fields = list(root)

        if len(fields) != 4:
            raise ValueError('Неверное количество полей XML')

        data = {}

        for element in fields:
            if element.tag in data or len(element) or element.attrib:
                raise ValueError('Некорректная структура XML')

            data[element.tag] = element.text

        data['year'] = int(data['year'])
        data['pages'] = int(data['pages'])

    else:
        raise ValueError('Неподдерживаемый формат')

    return validate_book(data)