from sshtunnel import SSHTunnelForwarder
from vk_api import VkApi
access_token = {"access_token": "xxxxx", "expires_in": 0, "user_id": 500000}
access_login = '+7xxxxxxxxxx'
access_password = 'xxxxxxx'

server = SSHTunnelForwarder(
    ('hostname.com', 22),
    ssh_username="username",
    ssh_pkey="id_rsa",
    ssh_private_key_password="",
    remote_bind_address=("127.0.0.1", 433),
    ssh_proxy_enabled=True
)
server.start()
proxies = dict(http=f'socks5://proxyuser@127.0.0.1:{server.local_bind_port}',
               https=f'socks5://proxyuser@127.0.0.1:{server.local_bind_port}')
vk_session = VkApi(login=access_login, password=access_password, token=access_token, proxies=proxies)
server.stop()