# **FOODGRAM API PRODJECT**

[![foodgram workflow](https://github.com/Mashka33/foodgram-project-react/actions/workflows/foodgram.yml/badge.svg)](https://github.com/Mashka33/foodgram-project-react/actions/workflows/foodgram.yml)

![python version](https://img.shields.io/badge/Python-3.9-green)
![django version](https://img.shields.io/badge/Django-2.2-green)
![Docker version](https://img.shields.io/badge/Docker-4.15-green)
![Djangorestframework version](https://img.shields.io/badge/Djangorestframework-3.12-green)
![PyJWT version](https://img.shields.io/badge/PyJWT-2.1-green)
![gunicornversion](https://img.shields.io/badge/gunicorn-12.7-green)

#### Проект доступен по эл.адресу:
http://51.250.82.45/admin/

## *Foodgram - продуктовый помощник*

<details>
<summary>
Настройка CI and CD
</summary>

для Linux-систем все команды необходимо выполнять от имени администратора
- Склонировать репозиторий
```bash
git clone https://github.com/Mashka33/yamdb_final.git
```
- Выполнить вход на удаленный сервер
- Установить docker на сервер:
```bash
apt install docker.io 
```
- Установить docker-compose на сервер:
```bash
curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```
- Локально отредактировать файл infra/nginx.conf, обязательно в строке server_name вписать IP-адрес сервера
- Скопировать файлы docker-compose.yml и nginx.conf из директории infra на сервер:
```bash
scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml
scp nginx.conf <username>@<host>:/home/<username>/nginx.conf
```
- Создать .env файл по предлагаемому выше шаблону.
- Для работы с Workflow добавить в Secrets GitHub переменные окружения для работы:
    ```
    DB_ENGINE=<django.db.backends.postgresql>
    DB_NAME=<имя базы данных postgres>
    DB_USER=<пользователь бд>
    DB_PASSWORD=<пароль>
    DB_HOST=<db>
    DB_PORT=<5432>
    
    DOCKER_PASSWORD=<пароль от DockerHub>
    DOCKER_USERNAME=<имя пользователя>
    
    SECRET_KEY=<секретный ключ проекта django>

    USER=<username для подключения к серверу>
    HOST=<IP сервера>
    PASSPHRASE=<пароль для сервера, если он установлен>
    SSH_KEY=<ваш SSH ключ (для получения команда: cat ~/.ssh/id_rsa)>

    TELEGRAM_TO=<ID чата, в который придет сообщение>
    TELEGRAM_TOKEN=<токен вашего бота>
    ```
    Workflow состоит из четырёх шагов:
     - Проверка кода на соответствие PEP8
     - Сборка и публикация образа бекенда на DockerHub.
     - Автоматический деплой на удаленный сервер.
     - Отправка уведомления в телеграм-чат.
- собрать и запустить контейнеры на сервере:
```bash
docker-compose up -d --build
```
- После успешной сборки выполнить следующие действия (только при первом деплое):
    * провести миграции внутри контейнеров:
    ```bash
    docker-compose exec web python manage.py migrate
</details>
<br />
<br />


### Описание проекта:

Проект представляет собой онлайн-сервис и API для него.
На этом сервисе пользователи могут публиковать рецепты, подписываться 
на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное»,
а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного
или нескольких выбранных блюд.

Дипломный проект факультета бэкенд-разработки [Яндекс.Практикума](https://practicum.yandex.ru/backend-developer)

## стек:
- Python
- Django
- Docker
- Nginx
- см. файл `backend/requirements.txt`

## руководство по установке Docker
можно найти [здесь](https://docs.docker.com/engine/install/)


---

### Запуск проекта на локальном компьютере:

#### Клонируйте репозиторий на свой компьютер и перейдите в корневую папку

`git clone https://github.com/Mashka33/foodgram-project-react.git`
`cd backend`

#### Установить виртуальное окружение

```
python -m venv venv

# Активировать виртуальное окружение

# для Linux
source env/bin/activate

# для Windows
source venv\Scripts\activate

# деактивировать виртуальное окружение можно командой
deactivate
```

#### Установить зависимости

```
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Шаблон наполнения .env файла по пути ```./infra/.env```

```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=username
POSTGRES_PASSWORD=password
DB_HOST=db
DB_PORT=5432
```

### описание команды для заполнения базы данными
```bash
cd backend && python manage.py loaddata ../infra/fixtures.json
```
### автор Степанова Мария https://github.com/Mashka33
