# encoding: utf-8


class VkTools(object):
    def __init__(self, vk):
        self.vk = vk

    def get_all_items(self, method, values=None, max_count=200):
        ''' Получить все элементы
            Работает в методах, где в ответе есть count и items

        :param method: метод
        :param values: параметры
        :param max_count: максимальное количество,
                            которое можно получить за один раз
        '''

        if not values:
            values = {}
        else:
            values = values.copy()

        values.update({'count': max_count})

        response = self.vk.method(method, values)
        count = response['count']
        items = response['items']

        for i in xrange(max_count, count + 1, max_count):
            values.update({
                'offset': i
            })

            response = self.vk.method(method, values)
            items += response['items']

        return {'count': len(items), 'items': items}
