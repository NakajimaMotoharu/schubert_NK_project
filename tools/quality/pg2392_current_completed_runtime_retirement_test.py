"""Independent literal644byte/metadata/effective declaration and real FD failure vectors."""
import inspect
import types
import unittest
import pg1223_completed_runtime_contract_test as fixture
from pg2392_current_completed_runtime_retirement_sources import sources,contract_source,BASE,SHA,TOOLS


class CurrentRetirement(unittest.TestCase):
    def test_exact_contract_all_field_and_actual_fd_faults(self):
        module=types.ModuleType('current_retirement');exec(contract_source(),module.__dict__)
        raw=inspect.getsource(fixture).replace('647','644');ns={**fixture.__dict__,'p':module};exec(compile(raw,'<literal644 fd vectors>','exec'),ns);ns['p']=module
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(ns['RuntimeContractTest']);result=unittest.TestResult();suite.run(result)
        self.assertEqual(3,result.testsRun);self.assertEqual([],result.errors);self.assertEqual([],result.failures)

    def test_actual_current17source_baseline_and_no_business_stop(self):
        values=sources();self.assertEqual(17,len(values))
        refs=values['pg2392_native_refs.py'];java=values['Pg2392NativeStop.java']
        for v in [BASE,SHA,'retirement.same_except_runtime']:self.assertIn(v,refs)
        self.assertNotIn('pg2392-current-resume-owned-stop-tools-v1','\n'.join(values.values()))
        self.assertIn('EXACT_COMPLETED_RUNTIME_RETIREMENT',java)
        self.assertIn('runtimeRetiredOnly=true',java)
        self.assertIn("[b'Pg2392NativeStop',b'retire',b'']",values['pg2392_native_owned_stop.py'])
        self.assertIn(TOOLS,refs+java)
        self.assertIn('zz-pg2316-once-resume.conf',contract_source())
        self.assertNotIn('pg1846',java)


if __name__=='__main__':unittest.main()
