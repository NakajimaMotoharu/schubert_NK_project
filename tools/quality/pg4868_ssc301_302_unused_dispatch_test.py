from contextlib import nullcontext
import json
import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
import pg4868_ssc301_302_unused_dispatch as role


class Dispatch(unittest.TestCase):
    def test_actual_entry_selects_fresh_current_and_new_candidate_once(self):
        seen=[]
        def namespace(candidate,before):seen.append((candidate,before));return {}
        with patch.object(role.sys,'argv',['tool','stage']),patch.object(role,'authenticate_host') as auth,patch.object(role,'runtime_namespace',side_effect=namespace),patch.object(role,'source',return_value='def main(): return 0'),patch.object(role,'management_gate',return_value=nullcontext()):
            self.assertEqual(0,role.main());auth.assert_called_once()
        self.assertEqual(1,len(seen));self.assertEqual(role.role.SOURCE,seen[0][0]['candidateSource'])
        self.assertEqual(role.role.CURRENT,seen[0][1]['productionSource']);self.assertEqual(role.role.BEFORE,seen[0][1]['privateBeforeSha256'])

    def test_all_runtime_guards_and_new_stage_namespaces(self):
        candidate=json.loads((role.role.W/'pg4860-candidate-build-v1.safe.json').read_bytes())
        before=role.before_record();ns=role.runtime_namespace(candidate,before)
        self.assertEqual(role.role.SOURCE,ns['SOURCE']);self.assertEqual(role.role.BEFORE,ns['BASELINE_SHA'])
        for key,value in [('runtimeAlreadyRetired',False),('dataOnlyNotRuntimeAuthority',False),('allClientAdvisoryFlock0',False),('allTenUnitsKernelEmpty',False),('privateBeforeSha256','0'*64)]:
            with self.subTest(key=key),self.assertRaises(ValueError):role.runtime_namespace(candidate,{**before,key:value})
        for raw in (role.stage_source(),role.source()):
            compile(raw,'<new once-only stage/place>','exec')
            self.assertNotIn('pg4710',raw);self.assertNotIn('PG4710',raw)
        self.assertIn('PG4868_IMMUTABLE_STAGE_V1',role.stage_source())
        with patch.object(role.sys,'argv',['tool','stop']),patch.object(role,'authenticate_host') as auth,self.assertRaises(ValueError):role.main()
        auth.assert_not_called()
        self.assertEqual(0,checkPath(role.__file__));self.assertEqual(0,checkPath(__file__))


if __name__=='__main__':unittest.main()
