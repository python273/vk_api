Пакет vk\_api
=============

Основной класс библиотеки
-------------------------

.. module:: vk_api.vk_api

.. autoclass:: VkApi
    :members:

.. autoclass:: VkUserPermissions
    :show-inheritance:
    :members:

Модуль для работы с аудио
-------------------------
.. module:: vk_api.audio
.. autoclass:: VkAudio
    :members:

Модуль для работы с longpoll
----------------------------

.. module:: vk_api.longpoll
.. autoclass:: VkLongPoll
    :members:
.. autoclass:: Event
    :members:
.. autoclass:: VkLongpollMode
    :members:
.. autoclass:: VkEventType
    :members:
.. autoclass:: VkPlatform
    :members:
.. autoclass:: VkOfflineType
    :members:
.. autoclass:: VkMessageFlag
    :members:
.. autoclass:: VkPeerFlag
    :members:

Модуль для работы с методом execute
-----------------------------------

.. module:: vk_api.execute
.. autoclass:: VkFunction
    :members:
    :special-members: __call__

Модуль для объединения запросов в один запрос execute
-----------------------------------------------------

.. module:: vk_api.requests_pool
.. autoclass:: VkRequestsPool
    :members:
.. autoclass:: RequestResult
    :members:

Модуль для выкачивания множества результатов
--------------------------------------------

.. module:: vk_api.tools
.. autoclass:: VkTools
    :members:

Модуль для загрузки медиаконтента в VK
--------------------------------------

.. module:: vk_api.upload
.. autoclass:: VkUpload
    :members:


Исключения, бросаемые библиотекой
---------------------------------

.. automodule:: vk_api.exceptions
    :members:
    :undoc-members:
    :show-inheritance:
