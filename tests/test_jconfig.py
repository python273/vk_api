from jconfig.memory import MemoryConfig


def test_config_section():
    c = MemoryConfig('secret')

    assert 'secret' in c._settings

    c.test = 'hello!'

    assert c['test'] == 'hello!'
    assert c.test == 'hello!'
    assert c._section == {'test': 'hello!'}

    c['test'] = '42'

    assert c['test'] == '42'
    assert c.test == '42'
    assert c._section == {'test': '42'}
