## Уведомления из Gitlab в Telegram

### Структура

- Данный проект использует функциональность Webhooks в Gitlab.
- При совершении события из Gitlab отправляется запрос на наш сервер с информацией о событии в виде json. В нашем случае используются уведомления о событиях в Issue (создание, редактирование, новый комментарий и тд).
- Для сервера с обработкой запросов из Gitlab будет использоваться сервис pythonanywhere.com, на котором будет развернуто веб приложение. Для создания веб приложение используется python-фреймворк Flask.

### Практическое применение

- Гибкая настройка уведомлений о событиях в issues
- Выгрузка информации по issues, например сроки исправления или была ли взята ошибка в работу
- Интаграция с Google sheets для сохранения всех заведенных ошибок аналитиками

### Необходимость использования

- Уменьшение времени реагирования аналитиком на новые комментарии в issue
- Упрощение работы с таблицами по ведению отчета об ошибках
