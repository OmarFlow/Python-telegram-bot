My first bot
============

Тестовое ридми

Установка
---------
Создайте виртуальноу окружени и активируйте его. Установите виртуальное окружение:

.. code-block:: text

    pip install -r requirements.txt

Настройка
---------
Создайте файл settings.py и добавьте туда следующие настройки:

.. code-block:: python

    PROXY = {'proxy_url': 'socks5:прокси:1080',
        'urllib3_proxy_kwargs': {'username':логин, 'password':пароль}
    }

    API_KEY = "Ключ который вы получили у BotFather"

    USER_EMOJI = [':smiley_cat:', ':smiling_imp:', ':panda_face:', ':dog:']

Запуск
------
В активированном виртуальном окружении выполните:

.. code-block:: text

    python3 first_bot.py