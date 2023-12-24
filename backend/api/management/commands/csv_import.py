import csv
import os
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


def get_reader(file_name: str):
    csv_path = os.path.join(settings.BASE_DIR, 'data/', file_name)
    csv_file = open(csv_path, encoding='utf-8')
    csv_reader = csv.reader(csv_file, delimiter=',')
    return csv_reader


class Command(BaseCommand):
    help = 'Загрузка данных из .csv'

    def handle(self, *args: Any, **options: Any) -> str:
        if Ingredient.objects.all().count() > 0:
            print('Данные уже были загружены')
            return

        reader = get_reader('ingredients.csv')
        next(reader, None)
        for row in reader:
            obj, created = Ingredient.objects.get_or_create(
                name=row[0],
                measurement_unit=row[1]
            )
        print('Данные из файла category.csv загружены в БД')
