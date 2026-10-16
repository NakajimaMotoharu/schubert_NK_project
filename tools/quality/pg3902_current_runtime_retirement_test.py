"""Independent real FD/negative contract and protected complete current17 sources."""
import ast
from collections import Counter
import inspect
import json
import types
import unittest
from unittest.mock import patch
from pg1446_current_cold_stage import W
from immutable_payload_binding import PROTECTED
import pg3902_current_runtime_retirement_sources as actual
import pg1223_completed_runtime_contract_test as fixture


def capsules(values):
    return Counter(ast.get_source_segment(raw,node)for name,raw in values.items()if name.endswith('.py')for node in ast.walk(ast.parse(raw))if isinstance(node,ast.Assign)and any(isinstance(t,ast.Name)and t.id in PROTECTED for t in node.targets))


class Retirement(unittest.TestCase):
    def test_exact644_real_fd_and_allfield_negative_oracles(self):
        module=types.ModuleType('current_exact_runtime');exec(actual.contract_source(),module.__dict__)
        namespace={**fixture.__dict__,'p':module}
        exec(compile(inspect.getsource(fixture).replace('647','644'),'<independent current644 real FD vectors>','exec'),namespace);namespace['p']=module
        result=unittest.TestResult();unittest.defaultTestLoader.loadTestsFromTestCase(namespace['RuntimeContractTest']).run(result)
        self.assertEqual(3,result.testsRun);self.assertEqual([],result.errors+result.failures)
        self.assertEqual(actual.RUNTIME_SHA,module.SHA);self.assertEqual('zz-pg3844-once-resume.conf',module.NAME)

    def test_complete_seventeen_preserves_every_old_capsule(self):
        original=actual.stopped.sources();values=actual.sources();self.assertEqual(17,len(values))
        self.assertEqual(capsules(original),capsules(values))
        refs=values['pg3902_native_refs.py']
        for text in [actual.BASE,actual.SHA,'retirement.same_except_runtime','pg3902_completed_runtime_contract']:self.assertIn(text,refs)
        self.assertIn("[b'Pg3902NativeStop',b'retire',b'']",values['pg3902_native_owned_stop.py'])
        binding=next(ast.literal_eval(n.value)for n in ast.parse(values['pg3902_parent_receipt.py']).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='BINDING'for t in n.targets))
        self.assertEqual(json.loads((W/'pg3856-current-resume-live-binding-v1/manifest.safe.json').read_bytes())['binding'],binding)
        capture=next(n for n in ast.walk(ast.parse(refs))if isinstance(n,ast.FunctionDef)and n.name=='capture_data')
        ret=next(n.value for n in ast.walk(capture)if isinstance(n,ast.Return)and isinstance(n.value,ast.Dict))
        self.assertEqual({'units','configuration','rows','pid1','startup','originals','backup','extraDurable','unitFilesActual','runtime','native'},{ast.literal_eval(k)for k in ret.keys})

    def test_arbitrary_history_colliding_with_both_namespace_and_final_alias(self):
        original=actual.stopped.sources()
        name=next(k for k in original if k.endswith('_parent_receipt.py'))
        marker="PARTIAL_CHAIN="+repr({'text':'pg3876/Pg3876/PG3876/pg3902-current-resume-owned-tools-v1'})+'\n'
        original[name]+='\n'+marker
        with patch.object(actual.stopped,'sources',return_value=original):values=actual.sources()
        self.assertEqual(capsules(original),capsules(values))
        self.assertTrue(any(marker in value for value in values.values()))


if __name__=='__main__':unittest.main()
