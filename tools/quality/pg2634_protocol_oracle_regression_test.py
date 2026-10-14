import unittest
from pyflakes.api import check
from pg2634_protocol_oracle_regression import SERVER


class ProtocolRegression(unittest.TestCase):
    def test_exact_real_tests_static_counter_and_main_byte_gate(self):
        self.assertEqual(0, check('INPUT={}\n'+SERVER, '<real Protocol regression whole namespace>'))
        for marker in ['tests==82', 'len(xmls)==17', 'main==174', 'images[0]==images[1]',
                       "counters[k]['missed']==0", 'spotbugs:check', 'fullSixIntegrationPending']:
            self.assertIn(marker, SERVER)


if __name__=='__main__':
    unittest.main()
