def test_api(vk):
    api = vk.get_api()
    user_info = api.users.get(user_ids=1)
    assert isinstance(user_info, list)
    assert user_info[0]['id'] == 1
