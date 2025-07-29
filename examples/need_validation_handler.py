# -*- coding: utf-8 -*-
import re
import vk_api

import requests
import urllib.parse as urllib
from vk_api.utils import (
    search_re
)
from vk_api.exceptions import *

RE_CAPTCHA_SID = re.compile(r'name="captcha_sid" value="(\d+)"')



def return_capcha(url):
    key = input("Enter captcha code {0}: ".format(url)).strip()

    return key


def need_validation_handler(validation):
    """ Обработчик проверки безопасности при запросе API
        (https://vk.com/dev/need_validation)

    :param validation: исключение
    """
    response = None
    try:
        redirect_uri = validation.get_redirect_uri()
        url = redirect_uri.split('?')[0]
        query_data = urllib.parse_qs(urllib.urlparse(redirect_uri).query)

        # captcha or validate
        query_data['act'] = 'captcha'   # TODO 'captcha' or 'validate'

        response = requests.post(url, data=query_data)
        captcha_sid = None
        if response.ok:
            if query_data['act'] == 'captcha':
                captcha_sid = search_re(RE_CAPTCHA_SID, response.text)
                captcha_url = validation.get_url(captcha_sid)
            elif query_data['act'] == 'validate':
                phone = input("Enter phone number: ").strip()
                query_data.update({
                    'act': 'validate_phone',
                    'phone': '{}'.format(phone)
                })
                requests.post(url, data=query_data)
            else:
                return None
        else:
            return None

        if query_data['act'] == 'captcha':
            key = return_capcha(captcha_url)
        else:
            del query_data['phone']
            key  = input("Enter code: ").strip()
            query_data.update({
                'act': 'validate_code',
                'code': '{}'.format(key)
            })
            requests.post(url, data=query_data)
        response = validation.try_again(key, captcha_sid)

    except Exception:
        print('error my_need_validation_handler')
        return None

    return response



def main():
    """ Пример обработки валидатора """

    login, password = 'python@vk.com', 'mypassword'
    vk_session = vk_api.VkApi(
        login, password,
        need_validation_handler=need_validation_handler  # функция для обработки валидатора
    )

    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return

    # some code
    # ...


if __name__ == '__main__':
    main()
