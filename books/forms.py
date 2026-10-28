from django import forms
from datetime import date


class BookForm(forms.Form):
    title = forms.CharField(
        label='Название книги',
        max_length=100
    )

    author = forms.CharField(
        label='Автор',
        max_length=100
    )

    year = forms.IntegerField(
        label='Год издания',
        min_value=1450,
        max_value=date.today().year
    )

    pages = forms.IntegerField(
        label='Количество страниц',
        min_value=1
    )

    file_format = forms.ChoiceField(
        label='Формат файла',
        choices=[
            ('json', 'JSON'),
            ('xml', 'XML')
        ]
    )


class UploadFileForm(forms.Form):
    file = forms.FileField(
        label='Выберите JSON или XML файл'
    )