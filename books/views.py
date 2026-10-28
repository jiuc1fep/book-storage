from pathlib import Path
import uuid

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect

from .forms import BookForm, UploadFileForm
from .utils import (
    save_book,
    read_book,
    get_books_folder
)


# Страница добавления книги
def add_book(request):

    if request.method == 'POST':

        form = BookForm(request.POST)

        if form.is_valid():

            book = {
                'title': form.cleaned_data['title'],
                'author': form.cleaned_data['author'],
                'year': form.cleaned_data['year'],
                'pages': form.cleaned_data['pages']
            }

            file_format = form.cleaned_data['file_format']

            save_book(book, file_format)

            messages.success(
                request,
                'Книга успешно сохранена!'
            )

            return redirect('book_list')

    else:
        form = BookForm()

    return render(
        request,
        'books/add_book.html',
        {'form': form}
    )


# Страница загрузки файла
def upload_book(request):

    if request.method == 'POST':

        form = UploadFileForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            uploaded_file = form.cleaned_data['file']

            extension = Path(uploaded_file.name).suffix.lower()

            if extension not in ['.json', '.xml']:

                messages.error(
                    request,
                    'Разрешены только JSON и XML файлы'
                )

                return redirect('upload_book')

            # Ограничение размера файла: 1 МБ
            if uploaded_file.size > 1024 * 1024:

                messages.error(
                    request,
                    'Размер файла не должен превышать 1 МБ'
                )

                return redirect('upload_book')

            folder = get_books_folder()

            filename = f'{uuid.uuid4().hex}{extension}'
            filepath = folder / filename

            try:

                # Сохраняем файл частями
                with open(filepath, 'wb') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                # Проверяем содержимое
                read_book(filepath)

            except (ValueError, KeyError, TypeError,
                    UnicodeError, OSError,
                    __import__('json').JSONDecodeError,
                    __import__('xml.etree.ElementTree',
                               fromlist=['ParseError']).ParseError) as error:

                # Удаляем невалидный файл
                filepath.unlink(missing_ok=True)

                messages.error(
                    request,
                    f'Ошибка файла: {error}'
                )

                return redirect('upload_book')

            messages.success(
                request,
                'Файл успешно загружен!'
            )

            return redirect('book_list')

    else:
        form = UploadFileForm()

    return render(
        request,
        'books/upload_book.html',
        {'form': form}
    )


# Страница просмотра всех книг
def book_list(request):

    folder = get_books_folder()

    books = []

    files = sorted(folder.iterdir())

    for filepath in files:

        if not filepath.is_file():
            continue

        if filepath.suffix.lower() not in ['.json', '.xml']:
            continue

        try:

            book = read_book(filepath)

            book['filename'] = filepath.name

            books.append(book)

        except (ValueError, KeyError, TypeError,
                UnicodeError, OSError,
                __import__('json').JSONDecodeError,
                __import__('xml.etree.ElementTree',
                           fromlist=['ParseError']).ParseError):
            continue

    return render(
        request,
        'books/book_list.html',
        {'books': books}
    )