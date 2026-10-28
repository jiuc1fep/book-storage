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