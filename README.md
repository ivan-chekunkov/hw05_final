# Сайт Yatube

## Описание

Проект сайта Yatube с постами на различные темы. Включает в себя панель администратора, регистрация пользователей, 
возможность подписок и отписок на авторов, раздиление постов на группы, работа с постами (создание, редактирование, удаление), 
пагинация, модель отправки электронных сообщений пользователям, основные шаблоны для страниц сайта, хранение данных в базе SQLite.

## Установка
```bash
# Склонируйте репозиторий
git clone <название репозитория>

# Создайте виртуальное окружение и активируйте его
python -m venv venv
source venv/Scripts/activate

# Установите необходимые пакеты
pip install -r requirements.txt
```
## Локальный запуск
```bash
# Выполнить миграции
python yatube/manage.py makemigrations
python yatube/manage.py migrate

# Запустить сервер
python yatube/manage.py runserver
```