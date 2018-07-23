import os

import vk_api

vk = vk_api.VkApi(login=os.environ['LOGIN'], password=os.environ['PASSWORD'])
vk.auth(token_only=True)
api = vk.get_api()


def test_api():
    user_info = api.users.get(user_ids=1)
    assert isinstance(user_info, list)
    assert user_info[0]['id'] == 1
