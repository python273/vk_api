vk_api [![PyPI](https://img.shields.io/pypi/v/vk_api.svg)](https://pypi.org/project/vk_api/) ![Python 3.6, 3.7, 3.8](https://img.shields.io/pypi/pyversions/vk_api.svg)
=================================================================================================================================================================================
**vk_api** – Python модуль для создания скриптов для ВКонтакте (vk.com API wrapper)

* [Документация](https://vk-api.readthedocs.io/en/latest/)
* [Примеры](./examples)
* [Чат в Telegram](https://t.me/python273_vk_api)
* [Документация по методам API](https://vk.com/dev/methods)
* [Альтернативы vk_api](https://github.com/python273/vk_api/issues/356) (асинхронность; боты)

```python
import vk_api

vk_session = vk_api.VkApi('+71234567890', 'mypassword')
vk_session.auth()

vk = vk_session.get_api()

print(vk.wall.post(message='Hello world!'))
```

Установка
------------
    $ pip3 install vk_api
