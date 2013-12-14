# encoding: utf-8
import json


class VkTools(object):
    def __init__(self, vk):
        self.vk = vk

    def get_all_items(self, method, values=None, max_count=200):
        ''' Получить все элементы
            Работает в методах, где в ответе есть count и items
            За один запрос получает max_count * 25 элементов

        :param method: метод
        :param values: параметры
        :param max_count: максимальное количество элементов,
                            которое можно получить за один раз
        '''

        if values:
            values = values.copy()
        else:
            values = {}

        items = []
        offset = 0

        while True:
            run_code = code_get_all_items % (max_count, offset, json.dumps(values), method, method)

            try:
                response = self.vk.method('execute', {'code': run_code})
            except Exception as e:
                print run_code
                print e

            items += response['items']

            if response['end']:
                break

            offset = response['offset']

        return {'count': len(items), 'items': items}

    def get_all_items_slow(self, method, values=None, max_count=200):
        ''' Получить все элементы
            Работает в методах, где в ответе есть count и items

        :param method: метод
        :param values: параметры
        :param max_count: максимальное количество элементов,
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

# Полный код в файле vk_procedures
code_get_all_items = 'var z=%s,x=%s,y=%s,p={"count":z}+y,r=API.%s(p),c=r["count"],j=r["items"],o=z,i=1;while(i<25&&o<c){o=i*z+x;p={"count":z,"offset":o}+y;r=API.%s(p);j=j+r["items"];i=i+1;};return{"count":c,"items":j,"offset":o,"end":o+z>=c};'
