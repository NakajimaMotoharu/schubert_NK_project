import unittest
from pyflakes.api import check
import pg5990_web_contract_selected as t


class Current24WebRunnerTest(unittest.TestCase):
    def test_all_source_methods_and_complete_generated_namespace(self):
        raw = t.runner_source(); names = sorted(k for k in vars(t.previous.previous.previous.engine) if k.isidentifier() and not k.startswith('__') and k != 'main')
        self.assertEqual(0, check('='.join(names)+'=None\nNODE_PATH=NODE_SHA=COUNTS=None\n'+raw,'<complete Web24 namespace>'))
        self.assertIn('len(target_counters)==24',raw); self.assertNotIn('head=SOURCE',raw)
        _cases, counts, targets = t.inventory()
        self.assertEqual((149,921,24),(len(counts),sum(counts.values()),len(targets['web'])))
        self.assertIn('os.pathsep+NODE_PATH',raw)


if __name__ == '__main__':
    unittest.main()
