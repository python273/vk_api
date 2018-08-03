Документация vk_api
===================

vk_api – Python модуль для написания скриптов для социальной сети Вконтакте
(vk.com) (API wrapper)

`Установка через PIP
<https://pythonworld.ru/osnovy/pip.html>`_:

.. code-block:: shell-session

   $ pip install --user vk_api

или

.. code-block:: shell-session

   # pip install vk_api

Примеры по использованию библиотеки доступны на `GitHub <https://github.com/python273/vk_api/tree/master/examples>`_.

.. code-block:: python

   import vk_api

   vk_session = vk_api.VkApi('+71234567890', 'mypassword')
   vk_session.auth()

   vk = vk_session.get_api()

   print(vk.wall.post(message='Hello world!'))


.. toctree::
   :maxdepth: 4
   :caption: Содержание:

   vk_api
   upload
   tools
   longpoll
   bot_longpoll
   keyboard
   audio
   streaming
   requests_pool
   execute
   enums
   exceptions
   jconfig


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
