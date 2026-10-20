import unittest
from pyflakes.api import check
import pg5922_current_catch_facts as t


class MainOnlyCatchInputTest(unittest.TestCase):
    def test_namespace_and_parser_flags_without_invoking_production(self):
        raw = t.input_source()
        self.assertIn('len(current)!=851', raw); self.assertIn('len(physical)!=1666', raw)
        self.assertIn('pg5912-api-expression-selected35-v1', raw)
        defined = '\n'.join(n+'=None' for n in vars(t.inputs_engine) if n.isidentifier() and not n.startswith('__') and n != 'inputs')+'\n'
        self.assertEqual(0, check(defined+raw, '<complete Main-only input namespace>'))
        helper = (t.engine.ROOT / 'tools/quality/SourceCatchContextInventory.java').read_text()
        self.assertIn('"-proc:none"', helper); self.assertIn('"-implicit:none"', helper)
        self.assertIn('task.parse()', helper); self.assertIn('task.analyze()', helper)
        self.assertNotIn('Class.forName', helper)


if __name__ == '__main__':
    unittest.main()
