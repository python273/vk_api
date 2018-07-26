from vk_api import VkRequestsPool, vk_request_one_param_pool


def test_requests_pool(vk):
    with VkRequestsPool(vk) as pool:
        users = pool.method('users.get', {'user_ids': 'durov'})
        error_request = pool.method('invalid.method')

    assert users.ok
    assert isinstance(users.result, list)
    assert users.result[0]['id'] == 1

    assert not error_request.ok


def test_requests_pool_one_param(vk):
    users, error = vk_request_one_param_pool(
        vk,
        'users.get',
        key='user_ids',
        values=['durov', 'python273'],
        default_values={'fields': 'city'}
    )

    assert error == {}
    assert isinstance(users, dict)
    assert users['durov'][0]['city']['id'] == 2
    assert users['python273'][0]['id'] == 183433824
