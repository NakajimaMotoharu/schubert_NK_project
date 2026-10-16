"""Independent physical module completeness, no NoTests suppression, exact target qualification."""
import unittest
from pyflakes.api import check,checkPath
import pg4670_root_identity_reactor_selection as selection


class ReactorSelection(unittest.TestCase):
    def test_physical_suites_and_missing_foreign_modules(self):
        selection.validate_selection(selection.MODULES,selection.template.ROOT)
        for module in ['protocol','storage','bootstrap','api','web','batch']:
            bad={k:v for k,v in selection.MODULES.items()if v!=module}
            with self.subTest(module=module),self.assertRaises(ValueError):selection.validate_selection(bad,selection.template.ROOT)
        bad={**selection.MODULES,'dev.codex.schubert.nk.api.UnknownTest':'api'}
        with self.assertRaises(ValueError):selection.validate_selection(bad,selection.template.ROOT)

    def test_exact_generated_scope_and_preserved_failure_gate(self):
        raw=selection.source()
        self.assertIn('module = MODULES[name]',raw)
        self.assertNotIn('failIfNoTests=false',raw)
        self.assertIn('if actual != expected',raw)
        self.assertIn('target identity conditions incomplete',raw)
        self.assertIn("'targetMethodCoverage':method_counters",raw)
        ns='\n'.join(n+'=None'for n in ['os','SOURCE','ROOT','WORK','tarfile','TESTS','MODULES','re','TOOLCHAIN','subprocess','datetime','Path','hashlib','ET','json','sha'])+'\n'
        self.assertEqual(0,check(ns+raw,'<whole emitted actual selection>'))
        self.assertEqual(0,checkPath(selection.__file__));self.assertEqual(0,checkPath(__file__))


if __name__=='__main__':unittest.main()
