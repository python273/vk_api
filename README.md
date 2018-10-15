vk_api [![PyPI](https://img.shields.io/pypi/v/vk_api.svg)](https://pypi.org/project/vk_api/) ![Python 2.7, 3.4, 3.5, 3.6, 3.7](https://img.shields.io/pypi/pyversions/vk_api.svg)
=================================================================================================================================================================================
**vk_api** – Python модуль для написания скриптов для социальной сети Вконтакте (vk.com) (API wrapper)

* [Документация](https://vk-api.readthedocs.io/en/latest/)
* [Примеры использования](./examples) (python3)
* [Документация по методам API](https://vk.com/dev/methods)

```python
import vk_api

vk_session = vk_api.VkApi('+71234567890', 'mypassword')
vk_session.auth()

vk = vk_session.get_api()

print(vk.wall.post(message='Hello world!'))
```

Установка
------------
    $ pip install vk_api
