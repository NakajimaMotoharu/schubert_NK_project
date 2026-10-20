import unittest
from pyflakes.api import check
import pg5976_web_form_selected as t


class Web921DefinitionTest(unittest.TestCase):
    def test_exact_semantic_inventory_source_methods_and_strict_current_counters(self):
        cases, counts, targets = t.inventory()
        self.assertEqual(143, len(cases['web'])); self.assertEqual(149, len(counts)); self.assertEqual(921, sum(counts.values())); self.assertEqual(12, len(targets['web']))
        raw = t.runner_source(); names = sorted(k for k in vars(t.previous.engine) if k.isidentifier() and not k.startswith('__') and k != 'main')
        self.assertEqual(0, check('='.join(names)+'=None\nCOUNTS=None\n'+raw, '<pure web921 definition>'))
        self.assertIn('len(target_counters)==12', raw); self.assertIn("'actualExit':0 if done else 1", raw)
        self.assertNotIn('systemctl', raw); self.assertNotIn('qemu-system', raw)


if __name__ == '__main__':
    unittest.main()
