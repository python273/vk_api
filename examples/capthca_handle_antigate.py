# -*- coding: utf-8 -*-
import vk_api
from antigate import AntiGate
import urllib
#надо зарегистрироваться на anti-captcha.com и получить api ключ
api_key_antigate = 'my_api_key'

def solve_captcha(url):
    resource = urllib.urlopen(url)
    out = open('captcha_tmp.jpeg', 'wb')
    out.write(resource.read())
    out.close()
    return AntiGate(api_key_antigate, 'captcha_tmp.jpeg').captcha_result


def captcha_handler_antigate(captcha):
    """ При возникновении капчи вызывается эта функция и ей передается объект
        капчи. Через метод get_url можно получить ссылку на изображение.
        Через метод try_again можно попытаться отправить запрос с кодом капчи
    """
    url = captcha.get_url()
    key = solve_captcha(url)
    return captcha.try_again(key)


def main():
    """ Пример обработки капчи """

    login, password = 'python@vk.com', 'mypassword'
    vk_session = vk_api.VkApi(
        login, password,
        captcha_handler=captcha_handler_antigate  # функция для обработки капчи
    )

    # some code
    # ...

if __name__ == '__main__':
    main()
