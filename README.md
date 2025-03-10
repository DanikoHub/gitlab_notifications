# Уведомления из Gitlab в Telegram

## 📌Основная информация о проекте

- Данный проект использует функциональность Webhooks в Gitlab
- При совершении события в Gitlab (ответ на комментарий, создание issue, изменение лейблов, назначение новых сотрудников и тд) отправляется запрос на сервер с информацией о событии
- После обработки полученных данных отправляется запрос к Telegram API, после чего выбранные пользователи получают уведомление о событии

### 🚀Стек технологий

- Python - язык программирования проекта
- Telebot - python фреймворк для работы с Telegram API
- SQLAlchemy - python библиотека для работы с запросами к БД
- Flask - python фреймворк для создания веб-приложений

- PostgreSQL - Основная СУБД проекта

- Docker - контейнеризация проекта

### 🔔Практическое применение

- Гибкая настройка уведомлений о событиях в issues
- Выгрузка информации по issues, к примеру сроки исправления, актуальные лейблы или была ли взята ошибка в работу
- Интеграция с Google sheets для сохранения заведенных ошибок

## Запуск проекта

1. Необходимо создать файл `.env` и указать в нем переменные окружения, для примера можно использовать файл `env.example`

3. Запустить проект через Docker
```bash
docker build -t gitlab-telegram-bot .
docker run -p 5000:5000 --env-file .env gitlab-telegram-bot
```


