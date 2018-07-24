from vk_api.execute import VkFunction


def test_execute(vk):
    func_add = VkFunction('return %(x)s + %(y)s;', args=('x', 'y'))
    func_get = VkFunction(
        'return API.users.get(%(values)s)[0]["id"];',
        args=('values',)
    )

    assert func_add(vk, 2, 6) == 8
    assert func_get(vk, {'user_ids': 'durov'}) == 1
