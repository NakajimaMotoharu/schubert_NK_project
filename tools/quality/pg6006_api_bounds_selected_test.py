import unittest
from pyflakes.api import check
import pg6006_api_bounds_selected as t


class CurrentApi15NormalRunnerTest(unittest.TestCase):
    def test_actual169source_methods_and_complete1021_namespace(self):
        raw=t.runner_source();names=sorted(k for k in vars(t.previous.engine)if k.isidentifier()and not k.startswith('__')and k!='main')
        self.assertEqual(0,check('='.join(names)+'=None\nNODE_PATH=NODE_SHA=COUNTS=None\n'+raw,'<complete API15 normal namespace>'))
        _cases,counts,targets=t.inventory()
        self.assertEqual((175,1021,15),(len(counts),sum(counts.values()),len(targets['api'])))
        self.assertIn('len(target_counters)==15',raw);self.assertIn('os.pathsep+NODE_PATH',raw)


if __name__=='__main__':unittest.main()
