# Дипломный проект Foodgram

## Описание проекта:
Сервис позволяет пользователям публиковать рецепты, добавлять чужие рецепты в избранное
и подписываться на публикации других авторов. Пользователям также доступен сервис «Список покупок».
Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Установка проекта ОС Ubuntu.
```bash
git pull
``` 
- Переименуйте .env.example в .env
```bash
cp .env.example .env
```
- Заполните его своими параметрами
```bash
nano .env
```
- Установите docker
- Установите nginx
- Установите certbot
- Сконфигурируйте nginx так, чтобы все запросы проксировались на контейнер с проектом.
- Настройте обслуживание SSL через certbot.
- запустите *docker compose*
```bash
sudo docker compose up --build
```

Внимание! Во время установки контейнеров автоматически запускаются миграции и скрипт по наполнению базы ингредиентами. При первом запуске нужно будет предварительно подключиться к контейнеру и создать БД в соответствии с теми параметрами, которые прописаны в .env

Для создания БД выполните команду:
```bash
sudo docker exec -it <container-db> psql -U postgres
CREATE DATABASE <database-name>;
exit
```

где **container-db** - это id контейнера присвоенного для базы данных (db), **database-name** - имя базы данных

После создания бд следует перезапустить docker compose чтобы миграции и наполнение автоматически запустилось
```bash
sudo docker compose down & sudo docker compose up --build 
```

Далее, создайте суперпользователя (админа) подключившись к контейнеру backend, выполнив команду
```bash
sudo docker exec -it <container_id> python manage.py createsuperuser
```

## Стек используемых технологий
- backend: фреймворк python **Django**
- fontend: фреймворк **ReactJS** (предоставлен)
- База данных: **PostgreSQL**
- Менеджер контейнеров: **Docker**
- Менеджер статики: **Nginx**

## Как наполнить БД данными
Ингредиенты заполнятся автоматически. Необходимо создать суперпользоватля для администрирования. Рецепты заполнять после регистрации пользователя штатным функционалом сайта

## Сведения о текущей публикации проекта

- Сайт: https://fg.hopto.org/
- Админка: https://fg.hopto.org/admin/
- Документация по API: http://localhost/api/docs/redoc.html

## Вход для ревью:
- Логин: **admin@admin.com**
- Пароль: **admin11111**

## Об Авторе
Наиля Морданшина

