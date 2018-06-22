# -*- coding: utf-8 -*-
import vk_api
from requests.adapters import HTTPAdapter


class MyHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = kwargs['timeout']
        super(MyHTTPAdapter, self).__init__(*args, **kwargs)

    def send(self, *args, **kwargs):
        kwargs['timeout'] = self.timeout
        return super(MyHTTPAdapter, self).send(*args, **kwargs)


def main():
    login, password = 'python@vk.com', 'mypassword'
    vk_session = vk_api.VkApi(login, password)

    # Proxies:
    vk_session.http.proxies = {
        'http': 'http://127.0.0.1:8080/',
        'https': 'https://127.0.0.1:8080/'
    }

    # Retries:
    vk_session.http.mount('https://', HTTPAdapter(max_retries=10))

    # Retries + timeout:
    vk_session.http.mount('https://', MyHTTPAdapter(max_retries=10, timeout=8))

    # ...


if __name__ == '__main__':
    main()
