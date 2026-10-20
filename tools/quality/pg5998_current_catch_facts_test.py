import unittest
from pyflakes.api import check
import pg5998_current_catch_facts as t


class CurrentMainTypeInputBindingTest(unittest.TestCase):
    def test_complete_namespace_and_all_main_fixed_source_guards(self):
        raw=t.input_source();names=sorted(k for k in vars(t.inputs_engine) if k.isidentifier() and not k.startswith('__') and k!='inputs')
        self.assertEqual(0,check('='.join(names)+'=None\nSTATIC_SHA=None\n'+raw,'<actual current Main namespace>'))
        self.assertIn('len(current)!=851',raw);self.assertIn('len(physical)!=1666',raw)
        self.assertIn('PG5992-web-contract-static-v1',raw);self.assertIn('pg5990-web-contract-selected921-v1/source',raw)


if __name__=='__main__':
    unittest.main()
