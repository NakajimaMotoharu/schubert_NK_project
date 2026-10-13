"""Actual held-file 644-byte retirement contract and all generated full-scope source closure."""
import unittest
import inspect
import types
import pg1223_completed_runtime_contract_test as historical
from pg2050_fresh_completed_runtime_retirement_sources import sources,contract_source


class Retirement(unittest.TestCase):
    def test_actual_contract_all_fields_and_real_fd_faults(self):
        module=types.ModuleType('actual_current_runtime_contract');exec(contract_source(),module.__dict__)
        raw=inspect.getsource(historical).replace('647','644')
        ns={**historical.__dict__,'p':module};exec(compile(raw,'<independent literal644 and actual FD vectors>','exec'),ns);ns['p']=module
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(ns['RuntimeContractTest']);result=unittest.TestResult();suite.run(result)
        self.assertEqual(3,result.testsRun);self.assertEqual([],result.errors);self.assertEqual([],result.failures)

    def test_actual_exact_file_and_generated_scope_without_business_restart(self):
        raw=contract_source();self.assertTrue('zz-pg1980-once-resume.conf'in raw);self.assertTrue('len(data)==644'in raw)
        self.assertTrue('78f1488383951e0fc2716bcf63ab41f75c64e975440e7f5e079fd6129f8612ec'in raw)
        values=sources();self.assertEqual(17,len(values))
        refs=values['pg2050_native_refs.py'];java=values['Pg2050NativeStop.java']
        self.assertTrue('EXACT_COMPLETED_RUNTIME_RETIREMENT'in java)
        self.assertTrue('runtimeRetiredOnly=true'in java)
        self.assertTrue('retirement.same_except_runtime' in refs)
        self.assertTrue('pg2030-native-stop-v1/after.private.json'in refs)
        self.assertTrue('c6d5f275a1a756a635655c3c4f6b3da22f4ce5c98b093efabdaab210fa2927ca'in refs)
        self.assertTrue("[b'Pg2050NativeStop',b'retire',b'']"in values['pg2050_native_owned_stop.py'])


if __name__=='__main__':unittest.main()
