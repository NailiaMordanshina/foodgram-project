# Дипломный проект Foodgram, «Продуктовый помощник»

## Описание проекта:
Сервис позволяет пользователям публиковать рецепты, добавлять чужие рецепты в избранное
и подписываться на публикации других авторов. Пользователям также доступен сервис «Список покупок».
Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Установка проекта
Для установки проекта потребуется каталог infra из проекта, дальнейшие инструкции будут актуальны для ОС Ubuntu.
- Скопируйте файлы из каталога infra 
- Переименуйте .env.example в .env
```bash
rm .env.example .env
```
- Заполните его своими параметрами
```bash
nano .env
```
- Установите [docker](https://docs.docker.com/engine/install/ubuntu/)
- Установите [nginx](https://www.nginx.com/resources/wiki/start/topics/tutorials/install/)
- Установите [certbot](https://certbot.eff.org/)
- Сконфигурируйте nginx так, чтобы все запросы проксировались на контейнер с проектом. И настройте обслуживание SSL через certbot. Пример настройки nginx и certbot можно посмотреть в исходниках проекта в /etc/default
- запустите *docker compose*
```bash
sudo docker compose up --build
```
Во время установки будут созданы контейнеры backend, nginx и db им будут присвоены имена, посмотреть список контейнеров можно командой
```bash
sudo docker ps
```

Внимание! Во время установки контейнеров автоматически запускаются миграции и скрипт по наполнению базы ингредиентами. При первом запуске нужно будет предварительно подключиться к контейнеру и создать БД в соответствии с теми параметрами, которые прописаны в .env

Для создания БД выполните команду:
```bash
sudo docker exec -it <container-db> psql -U postgres
CREATE DATABASE <database-name>;
exit
```

где **container-db** - это имя контейнера присвоенного для базы данных (db), **database-name** - имя базы данных

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
Ингредиенты заполнятся автоматически. Рецепты заполнять после регистрации пользователя штатным функционалом сайта

## Сведения о текущей публикации проекта

- Сайт: https://fasol.hopto.org
- Админка: Для разворачивания проекта потребуется каталог infra из проекта, дальнейшие инструкции будут актуальны для ОС Ubuntu.
- Скопируйте файлы из каталога infra 
- Переименуйте .env.example в .env
```bash
rm .env.example .env
```
- Заполните его своими параметрами
```bash
nano .env
```
- Установите [docker](https://docs.docker.com/engine/install/ubuntu/)
- Установите [nginx](https://www.nginx.com/resources/wiki/start/topics/tutorials/install/)
- Установите [certbot](https://certbot.eff.org/)
- Сконфигурируйте nginx так, чтобы все запросы проксировались на контейнер с проектом. И настройте обслуживание SSL через certbot. Пример настройки nginx и certbot можно посмотреть в исходниках проекта в /etc/default
- запустите *docker compose*
```bash
sudo docker compose up --build
```
Во время разворачивания будут созданы контейнеры backend, nginx и db им будут присвоены имена, посмотреть список контейнеров можно командой
```bash
sudo docker ps
```

Внимание! Во время разворачивания контейнеров автоматически запускаются миграции и скрипт по наполнению базы ингредиентами. При первом запуске нужно будет предварительно подключиться к контейнеру и создать БД в соответствии с теми параметрами, которые прописаны в .env

Для создания БД выполните команду:
```bash
sudo docker exec -it <container-db> psql -U postgres
CREATE DATABASE <database-name>;
exit
```

где **container-db** - это имя контейнера присвоенного для базы данных (db), **database-name** - имя базы данных

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
Ингредиенты заполнятся автоматически. Рецепты заполнять после регистрации пользователя штатным функционалом сайта

## Сведения о текущей публикации проекта

- Сайт: https://fg.hopto.org/
- Админка: https://fg.hopto.org/admin/
- Документация по API: http://localhost/api/docs/redoc.html

## Вход для ревью:
- Логин: **admin@admin.com**
- Пароль: **admin11111**

## Об Авторе
Наиля Морданшина

