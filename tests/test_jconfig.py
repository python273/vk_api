import unittest
from jconfig.memory import MemoryConfig


class TestJconfig(unittest.TestCase):
    def test_config_section(self):
        c = MemoryConfig('secret')
        self.assertTrue('secret' in c._settings)

        c.test = 'hello!'
        self.assertTrue(c['test'] == 'hello!')
        self.assertTrue(c.test == 'hello!')
        self.assertTrue(c._section == {'test': 'hello!'})

        c['test'] = '42'
        self.assertTrue(c['test'] == '42')
        self.assertTrue(c.test == '42')
        self.assertTrue(c._section == {'test': '42'})


if __name__ == '__main__':
    unittest.main()
