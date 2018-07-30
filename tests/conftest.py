import os
import pytest

from vk_api import VkApi


@pytest.fixture
def vk():
    login = os.environ['LOGIN']
    password = os.environ['PASSWORD']
    vk = VkApi(login, password)
    vk.auth(token_only=True)
    return vk
