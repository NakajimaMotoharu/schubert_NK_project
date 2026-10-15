"""Literal contract, actual FD fault vectors, current target and preserved negative guards."""
import inspect
import types
import unittest
import pg1223_completed_runtime_contract_test as fixture
import pg3034_current_runtime_retirement_sources as current


class CurrentRetirement(unittest.TestCase):
    def test_actual644byte_contract_and_fd_vectors(self):
        module = types.ModuleType('actual_current_retirement')
        exec(current.contract_source(), module.__dict__)
        raw = inspect.getsource(fixture).replace('647', '644')
        ns = {**fixture.__dict__, 'p': module}
        exec(compile(raw, '<independent644byte realFD fault fixtures>', 'exec'), ns)
        ns['p'] = module
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(ns['RuntimeContractTest'])
        result = unittest.TestResult()
        suite.run(result)
        self.assertEqual(3, result.testsRun)
        self.assertEqual([], result.errors)
        self.assertEqual([], result.failures)
        self.assertEqual('zz-pg2970-once-resume.conf', module.NAME)
        self.assertEqual('abe8732db9bad858e6d1b27e541ded5f0d82bf68998c710a757464f4eee9fbbd', module.SHA)

    def test_actual17_sources_only_retirement_not_stop(self):
        values = current.sources()
        self.assertEqual(17, len(values))
        refs = values['pg3034_native_refs.py']
        java = values['Pg3034NativeStop.java']
        # The authoritative management baseline is the independently qualified
        # stopped image, not the earlier live four-owner seal.
        for token in [current.BASE, current.SHA, 'retirement.same_except_runtime']:
            self.assertTrue(token in refs, token)
        self.assertTrue('EXACT_COMPLETED_RUNTIME_RETIREMENT' in java)
        self.assertTrue("[b'Pg3034NativeStop',b'retire',b'']" in values['pg3034_native_owned_stop.py'])
        self.assertTrue('91f5484b-9702-4c7c-97f3-dd5110a853f9' in values['pg3034_parent_receipt.py'])
        self.assertTrue(current.TOOLS in refs + java)


if __name__ == '__main__':
    unittest.main()
