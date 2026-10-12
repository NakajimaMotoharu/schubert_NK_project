"""Actual current runtime contract: literal fields and held-FD fault oracle."""
import inspect
import types
import unittest
from pg1591_current_runtime_retirement_sources import contract_source,sources,SHA,BASE,TOOLS
import pg1223_completed_runtime_contract_test as historical_test

class CurrentRetirementTest(unittest.TestCase):
    def test_current_exact_contract_and_real_fd_all_faults(self):
        p=types.ModuleType('current_runtime_contract');exec(contract_source(),p.__dict__)
        self.assertEqual(p.RUN,'15700a87-9117-4f63-a0ff-768dd604d0f1')
        self.assertEqual(p.SHA,'2c20987e1457942dc196a1f591b4cd925bac1da2d689421a6782ba4d3eb31f35')
        self.assertEqual(p.TARGET,'/run/systemd/system/schubert-nk-morning-controller.service.d/zz-pg1160-once-resume.conf')
        ns={**historical_test.__dict__,'p':p};exec(compile(inspect.getsource(historical_test),'<current same qualified independent fixture>', 'exec'),ns)
        # Module source import is historical by construction; overwrite the
        # fixture global with the actual new contract, then execute all tests.
        ns['p']=p
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(ns['RuntimeContractTest'])
        result=unittest.TestResult();suite.run(result)
        self.assertEqual(result.testsRun,3);self.assertEqual(result.errors,[]);self.assertEqual(result.failures,[])

    def test_actual_full_refs_retirement_only_and_exact_normal_baseline(self):
        values=sources();self.assertEqual(len(values),16)
        refs=values['pg1591_native_refs.py'];java=values['Pg1591NativeStop.java']
        for literal in [SHA,BASE,"'native':tree(","retirement.retire_entry(","['before','retire','terminal','release']",'prior.items()',"capture_data(False)","h.kernel_empty(u)"]:
            self.assertIn(literal,refs)
        for bad in ['h.stop_one(',"action.startswith('stop:')","require(prior['source']"]:self.assertNotIn(bad,refs)
        self.assertIn('refs.check("retire")',java);self.assertNotIn('for(var unit:',java)
        self.assertIn('db.rollback();db.close();lease.confirmClosed()',java)
        self.assertIn(TOOLS,java)
        self.assertIn("[b'Pg1591NativeStop',b'retire',b'']",values['pg1591_native_owned_stop.py'])

if __name__=='__main__':unittest.main()
