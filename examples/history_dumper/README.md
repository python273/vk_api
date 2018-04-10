# VKHistoryDumper

## Установка

### postgresql

```
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
pip install psycopg2
sudo -u postgres psql
```

### history_dumper

```sh
virtualenv -p python3 venv
source venv/bin/activate
git clone https://github.com/xkord/vk_api
cd vk_api/examples/history_dumper
pip install -r requirements.txt
python setup.py install
```

## Подготовка к использованию

### Создание базы данных

```
CREATE DATABASE vk_history;
CREATE USER vk_user WITH password 'YOUR_PASSWORD';
GRANT ALL privileges ON DATABASE vk_history TO vk_user;
```

### Подготовка config файла

        VK_LOGIN = 'YOUR_VK_LOGIN'
        VK_PASSWORD = 'YOUR_VK_PASSWORD'
        DATABASE = 'vk_history'
        HOST = '127.0.0.1'
        USER = 'vk_user'
        PASSWORD_DB = 'YOUR_DB_PASSWORD'
        PORT = 5432

## Использование

```
history_dumper -c config -V
```
