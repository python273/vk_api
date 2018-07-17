import os
import unittest

from vk_api import VkApi
from vk_api.execute import VkFunction


class TestExecute(unittest.TestCase):
    def setUp(self):
        self.vk = VkApi(login=os.environ['LOGIN'], password=os.environ['PASSWORD'])
        self.vk.auth(token_only=True)

    def test_execute(self):
        self.func_add = VkFunction('return %(x)s + %(y)s;', args=('x', 'y'))
        self.func_get = VkFunction('return API.users.get(%(values)s)[0]["id"];',
                                   args=('values',))

        self.assertEqual(self.func_add(self.vk, 2, 6), 8)
        self.assertEqual(self.func_get(self.vk, {'user_ids': 'durov'}), 1)


if __name__ == '__main__':
    unittest.main()
