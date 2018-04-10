sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
pip install psycopg2

sudo -u postgres psql

CREATE DATABASE vk_history;
CREATE USER vk_user WITH password 'YOUR_PASSWORD';
GRANT ALL privileges ON DATABASE vk_history TO vk_user;