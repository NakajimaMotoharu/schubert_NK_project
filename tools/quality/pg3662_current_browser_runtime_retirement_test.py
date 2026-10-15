"""Current real-FD faults, exact17/full11 return, closed retire-only dispatcher and separate post."""
import ast
import inspect
import json
import types
import unittest
from pyflakes.api import check
from pg1446_current_cold_stage import W
import pg1223_completed_runtime_contract_test as fixture
import pg1257_fresh_independent_terminal_post as schema
import pg3662_current_browser_runtime_retirement_sources as current
import pg3666_current_browser_runtime_retirement_dispatch as dispatch
import pg3668_current_browser_runtime_retirement_post as post


class CurrentRetirement(unittest.TestCase):
    def test_fixed644_contract_real_fd_faults(self):
        module=types.ModuleType('current_runtime');exec(current.contract_source(),module.__dict__)
        ns={**fixture.__dict__,'p':module}
        exec(compile(inspect.getsource(fixture).replace('647','644'),'<independent held-FD fixture>','exec'),ns);ns['p']=module
        result=unittest.TestResult();unittest.defaultTestLoader.loadTestsFromTestCase(ns['RuntimeContractTest']).run(result)
        self.assertEqual(3,result.testsRun);self.assertEqual([],result.errors+result.failures)
        self.assertEqual('zz-pg3564-once-resume.conf',module.NAME);self.assertEqual(current.RUNTIME_SHA,module.SHA)

    def test_complete17_current_receipt_and_all11(self):
        values=current.sources();self.assertEqual(17,len(values));refs=values['pg3662_native_refs.py']
        for text in [current.BASE,current.SHA,'retirement.same_except_runtime']:self.assertIn(text,refs)
        self.assertIn("[b'Pg3662NativeStop',b'retire',b'']",values['pg3662_native_owned_stop.py'])
        binding=next(ast.literal_eval(n.value)for n in ast.parse(values['pg3662_parent_receipt.py']).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='BINDING'for t in n.targets))
        self.assertEqual(json.loads((W/'pg3576-current-browser-live-binding-v1/manifest.safe.json').read_bytes())['binding'],binding)
        capture=next(n for n in ast.walk(ast.parse(refs))if isinstance(n,ast.FunctionDef)and n.name=='capture_data')
        ret=next(n.value for n in ast.walk(capture)if isinstance(n,ast.Return)and isinstance(n.value,ast.Dict))
        self.assertEqual({'units','configuration','rows','pid1','startup','originals','backup','extraDurable','unitFilesActual','runtime','native'},{ast.literal_eval(k)for k in ret.keys})
        self.assertIn('require(all(same_value(first[k],v)for k,v in prior.items()))',refs)

    def test_final_current_dispatch_and_post(self):
        raw=dispatch.run_source()
        for text in ["('stage', 'retire')",'Pg3662NativeStop retire','pg3666-stage-v1.exit','pg3664-frozen-v1.safe.json']:self.assertIn(text,raw)
        self.assertNotIn('Pg3662NativeStop stop',raw)
        self.assertIn(dispatch.ARCHIVE,dispatch.STAGE);self.assertIn(dispatch.REMOTE,dispatch.STAGE)
        self.assertEqual(current.SHA,dispatch.context()[0]);self.assertEqual(0,check(dispatch.post_payload(),'<actual stopped pre-retire>'))
        proof=json.loads((W/'pg3606-current-browser-owned-post-v1/manifest.safe.json').read_bytes())
        raw=post.payload({n:proof['proofHashes'][n]['sha256']for n in schema.previous.SEALS})
        for text in ['same_except_runtime','prior_equal(json.loads(prior_raw),before,after)','zz-pg3564-once-resume.conf','exactRuntimeEntryRetired','pg3662-native-stop-v1']:self.assertIn(text,raw)
        for old in ['pg2392','pg2374','pg3006','pg3034','zz-pg3100']:self.assertNotIn(old,raw)


if __name__=='__main__':unittest.main()
