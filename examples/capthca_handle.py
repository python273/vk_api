# -*- coding: utf-8 -*-

"""
@author: Kirill Python
@contact: https://vk.com/python273
"""

import vk_api


def captcha_handler(captcha):
    key = input("Enter Captcha {0}: ".format(captcha.get_url())).strip()

    # Пробуем снова отправить запрос с капчей
    return captcha.try_again(key)


def main():
    """ Пример: обработка капчи """

    login, password = 'python@vk.com', 'mypassword'
    vk = vk_api.VkApi(
        login, password,
        captcha_handler=captcha_handler  # function for handle captcha
    )

    try:
        vk.authorization()
    except vk_api.AuthorizationError as error_msg:
        print(error_msg)
        return

    # some code
    # ...

if __name__ == '__main__':
    main()
