"""Actual normal RO evidence, full24 graph, exact immutable capsules and fail closed."""
import ast
from collections import Counter
import copy
import json
import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
from immutable_payload_binding import PROTECTED
from bundle_hash_contract import require_bound
import pg4722_ssc299_publication_sources as role
import pg4724_ssc299_publication_compile as compiler


def capsules(raw):
    return Counter(ast.get_source_segment(raw,n)for n in ast.walk(ast.parse(raw))
                   if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in PROTECTED for t in n.targets))


class FinitePublication(unittest.TestCase):
    def test_actual_normal_ro_twenty_four_and_immutable_current_original(self):
        self.assertTrue(role.qualify()['candidateHostReadonlyVerified'])
        ro=role.ro.sources();values=compiler.generated();self.assertEqual(24,len(values))
        for suffix in ['parent_receipt','warning_parent_projection']:
            self.assertEqual(capsules(ro['pg4714_'+suffix+'.py']),capsules(values['pg4722_'+suffix+'.py']))
        self.assertTrue(require_bound(values['pg4722_native_refs.py'],compiler.ro_compile.sha(compiler.ro_compile.PRIOR/'bundle.safe.json')))
        raw=compiler.compiler()
        for value in ['pg4724-frozen-v1.safe.json','pg4708-frozen-v1.safe.json',"('transition','TransitionTest')",'pg4432-release-v1/api/api.jar']:
            self.assertIn(value,raw)
        for name in ['pg1083_cold_publication_contract.py','pg1088_cold_exchange_io.py','pg1090_cold_finite_capture.py','pg2441_ordinary_exchange_io.py']:
            self.assertIn(name,values)

    def test_missing_foreign_bool_or_non_normal_receipt_never_publishes(self):
        original=json.loads((role.W/'pg4720-ssc299-ro-independent-post-v1/manifest.safe.json').read_bytes())
        for key,value in [('candidateHostReadonlyVerified',False),('candidateSource',role.CURRENT),
                          ('currentSource',role.SOURCE),('candidateManifestSha256','0'*64),
                          ('newTenReferencesReturnedNormally',False),('actualExit',False)]:
            bad=copy.deepcopy(original);bad['result'][key]=value
            with patch.object(role.ro,'qualify'),patch.object(role.json,'loads',return_value=bad):
                with self.subTest(key=key),self.assertRaises(ValueError):role.qualify()
        for path in [role.__file__,compiler.__file__,__file__]:self.assertEqual(0,checkPath(path))


if __name__=='__main__':unittest.main()
