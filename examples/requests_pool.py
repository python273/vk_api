# -*- coding: utf-8 -*-
import vk_api


def main():
    """ Пример работы с VkRequestsPool

        VkRequestsPool позволяет выполнять до 25 запросов к API за один запрос
        к серверу с помощью метода execute.
    """

    login, password = 'python@vk.com', 'mypassword'
    vk_session = vk_api.VkApi(login, password)

    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return

    with vk_api.VkRequestsPool(vk_session) as pool:
        friends = pool.method('friends.get')
        status = pool.method('status.get')

        # Пример запроса с ошибкой
        request_with_error = pool.method('wall.getById')

    """ Обратите внимание, что запрос выполняется после выхода из with
        и к результатам обратиться можно только после выхода из него
    """

    print(friends.result)
    print(status.result)

    # False - поэтому нельзя обратиться к результату
    print(request_with_error.ok)

    """ Пример получения друзей у нескольких пользователей за один запрос
    """

    friends = {}

    with vk_api.VkRequestsPool(vk_session) as pool:
        for user_id in [1, 183433824]:
            friends[user_id] = pool.method('friends.get', {
                'user_id': user_id,
                'fields': 'photo'
            })

    for key, value in friends.items():
        friends[key] = value.result

    print(friends)

    """ Следующий пример - оптимизированная версия предыдущего

        В friends будет записан тот же самый результат, что и в прошлом примере.
        method_one_param можно использовать, когда запрос идет к одному методу,
        и когда изменяется только один параметр. В данном случае это 'user_id'

        Плюс не нужно вызывать .result для каждого ключа
    """
    with vk_api.VkRequestsPool(vk_session) as pool:
        friends = pool.method_one_param(
            'friends.get',  # Метод
            key='user_id',  # Изменяющийся параметр
            values=[1, 183433824],

            # Параметры, которые будут в каждом запросе
            default_values={'fields': 'photo'}
        )

    print(friends.result)

if __name__ == '__main__':
    main()
