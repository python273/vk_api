# class VkApi(object):

## Methods defined here:
### \_\_init\_\_

- login (default: `None`) — Логин ВКонтакте (лучше использовать номер телефона для автоматического обхода проверки безопасности)
- password (default: `None`) — Пароль ВКонтакте (если пароль не передан, то будет попытка использовать сохраненные данные)
- token (default: `None`; type: `str`) — access_token
- auth_handler (default: `None`) — Функция для обработки двухфакторной аутентификации, должна возвращать строку с кодом и булевое значение, означающее, стоит ли запомнить это устройство, для прохождения аутентификации.
- captcha_handler (default: `None`) — Функция для обработки капчи
- config (default: `<class 'jconfig.jconfig.Config'>`) — Класс для сохранения настроек
- config_filename (default: `'vk_config.v2.json'`) — Расположение config файла
- api_version (default: `'5.63'`; type: `str`) — Версия API
- app_id (default: `2895443`; type: `int`) — Standalone-приложение
- scope (default: `33554431`; types: `int`, `str`) — Запрашиваемые права (можно передать строкой или числом)
- client_secret (default: `None`) — Защищенный ключ приложения для серверной авторизации ([https://vk.com/dev/auth_server](https://vk.com/dev/auth_server))

### api_login
 Получение токена через Desktop приложение

### auth
 Аутентификация
- reauth (default: `False`) — Позволяет переавторизиваться, игнорируя сохраненные куки и токен
- token_only (default: `False`) — Включает оптимальную стратегию аутентификации, если необходим только access_token Например если сохраненные куки не валидны, но токен валиден, то аутентификация пройдет успешно При token_only=False, сначала проверяется валидность куки. Если кука не будет валидна, то будет произведена попытка аутетификации с паролем. Тогда если пароль не верен или пароль не передан, то аутентификация закончится с ошибкой. Если вы не делаете запросы к веб версии сайта используя куки, то лучше использовать token_only=True

### auth_handler
 Обработчик двухфакторной аутентификации

### captcha_handler
 Обработчик капчи ([http://vk.com/dev/captcha_error](http://vk.com/dev/captcha_error))
- captcha — объект исключения `Captcha`

### check_sid
 Проверка Cookies remixsid на валидность

### check_token
 Проверка access_token на валидность

### get_api
 Возвращает VkApiMethod(self) Позволяет обращаться к методам API как к обычным классам. Например vk.wall.get(...)

### http_handler
 Обработчик ошибок соединения
- error — исключение

### method
 Вызов метода API
- method (type: `str`) — имя метода
- values (default: `None`; type: `dict`) — параметры
- captcha_sid (default: `None`) — id капчи
- captcha_key (default: `None`; type: `str`) — ответ капчи
- raw (default: `False`; type: `bool`) — при False возвращает `response['response']` при True возвращает `response` (может понадобиться для метода execute для получения execute_errors)

### need_validation_handler
 Обработчик проверки безопасности при запросе API ([http://vk.com/dev/need_validation](http://vk.com/dev/need_validation))
- error — исключение

### security_check
 Функция для обхода проверки безопасности (запрос номера телефона)
- response (default: `None`) — ответ предыдущего запроса, если есть

### server_auth
 Серверная авторизация

### too_many_rps_handler
 Обработчик ошибки "Слишком много запросов в секунду". Ждет пол секунды и пробудет отправить запрос заново
- error — исключение

### twofactor
 Двухфакторная аутентификация
- auth_response — страница с приглашением к аутентификации

### vk_login
 Авторизация ВКонтакте с получением cookies remixsid
- captcha_sid (default: `None`) — id капчи
- captcha_key (default: `None`; type: `str`) — ответ капчи

## Data and other attributes defined here:
**RPS_DELAY** = 0.34

