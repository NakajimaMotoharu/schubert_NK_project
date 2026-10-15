"""Independent realFD faults/current17 graph/actual receipt and closed transport."""
import ast
import inspect
import json
import types
import unittest
from pyflakes.api import check
from pg1446_current_cold_stage import W
import pg1223_completed_runtime_contract_test as fixture
import pg1257_fresh_independent_terminal_post as schema
import pg3192_browser_runtime_retirement_sources as current
import pg3196_browser_runtime_retirement_dispatch as dispatch
import pg3198_browser_runtime_retirement_post as post


class BrowserRetirement(unittest.TestCase):
    def test_fixed644_byte_contract_and_real_fd_failures(self):
        module = types.ModuleType('current_browser_runtime')
        exec(current.contract_source(), module.__dict__)
        ns = {**fixture.__dict__, 'p': module}
        exec(compile(inspect.getsource(fixture).replace('647', '644'), '<independent realFD vectors>', 'exec'), ns)
        ns['p'] = module
        result = unittest.TestResult()
        unittest.defaultTestLoader.loadTestsFromTestCase(ns['RuntimeContractTest']).run(result)
        self.assertEqual(3, result.testsRun)
        self.assertEqual([], result.errors + result.failures)
        self.assertEqual('zz-pg3100-once-resume.conf', module.NAME)
        self.assertEqual('abe8732db9bad858e6d1b27e541ded5f0d82bf68998c710a757464f4eee9fbbd', module.SHA)

    def test_all17_sources_actual_current_positive_receipt_and_full_snapshot(self):
        values = current.sources()
        self.assertEqual(17, len(values))
        refs = values['pg3192_native_refs.py']
        for literal in [current.BASE, current.SHA, 'retirement.same_except_runtime']:
            self.assertTrue(literal in refs, literal)
        self.assertTrue("[b'Pg3192NativeStop',b'retire',b'']" in values['pg3192_native_owned_stop.py'])
        tree = ast.parse(values['pg3192_parent_receipt.py'])
        binding = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'BINDING' for t in n.targets))
        actual = json.loads((W / 'pg3124-browser-resume-live-binding-v1/manifest.safe.json').read_bytes())['binding']
        self.assertEqual(actual, binding)
        for name, raw in values.items():
            if name.endswith('.py'):
                self.assertEqual(0, check(raw, '<complete17 ' + name + '>'))
        # Retire starts from the qualified stopped raw, not the earlier live seal.
        # Actual3156 raw has ten keys. Retirement captures native as an eleventh
        # value and keeps it equal throughout; independent prior_equal proves the
        # exact augmentation rather than silently dropping it (BUG1204/1266).
        capture = next(n for n in ast.walk(ast.parse(refs)) if isinstance(n, ast.FunctionDef) and n.name == 'capture_data')
        returns = [n for n in ast.walk(capture) if isinstance(n, ast.Return) and isinstance(n.value, ast.Dict)]
        self.assertEqual(1, len(returns))
        self.assertEqual({'units','configuration','rows','pid1','startup','originals','backup','extraDurable','unitFilesActual','runtime','native'}, {ast.literal_eval(k) for k in returns[0].value.keys})
        self.assertTrue('require(all(same_value(first[k],v)for k,v in prior.items()))' in refs)

    def test_dispatch_and_independent_post_are_current_complete(self):
        raw = dispatch.run_source()
        for literal in ["('stage', 'retire')", 'Pg3192NativeStop retire', 'pg3196-stage-v1.exit', 'pg3194-frozen-v1.safe.json']:
            self.assertTrue(literal in raw, literal)
        self.assertFalse('Pg3192NativeStop stop' in raw)
        self.assertTrue(dispatch.ARCHIVE in dispatch.STAGE)
        self.assertTrue(dispatch.REMOTE in dispatch.STAGE)
        self.assertEqual(current.SHA, dispatch.context()[0])
        self.assertEqual(0, check(dispatch.post_payload(), '<current stopped pre-retire whole>'))
        proof = json.loads((W / 'pg3156-browser-business-owned-post-v1/manifest.safe.json').read_bytes())
        raw = post.payload({n: proof['proofHashes'][n]['sha256'] for n in schema.previous.SEALS})
        for literal in ['same_except_runtime', 'prior_equal(json.loads(prior_raw),before,after)', 'zz-pg3100-once-resume.conf', 'exactRuntimeEntryRetired', 'pg3192-native-stop-v1']:
            self.assertTrue(literal in raw, literal)
        for old in ['pg2392', 'pg2374', 'pg3006', 'pg3034', 'zz-pg2970']:
            self.assertFalse(old in raw, old)


if __name__ == '__main__':
    unittest.main()
