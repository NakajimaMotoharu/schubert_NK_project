"""Actual unused post as prerequisite, distinct candidate/current and immutable data."""
import ast
from collections import Counter
import copy
import json
import unittest
from unittest.mock import patch
from pyflakes.api import check,checkPath
from immutable_payload_binding import PROTECTED
from bundle_hash_contract import require_bound
import pg4714_ssc299_ro_sources as role
import pg4716_ssc299_ro_compile as compiler


def capsules(raw):
    return Counter(ast.get_source_segment(raw,n)for n in ast.walk(ast.parse(raw))
                   if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in PROTECTED for t in n.targets))


class NormalRo(unittest.TestCase):
    def test_actual_post_all18_and_same_original_capsules_and_single_bundle(self):
        self.assertTrue(role.qualify()['candidateUnusedOnly'])
        normal=role.unused.sources();values=compiler.generated()
        self.assertEqual(18,len(values))
        for suffix in ['parent_receipt','warning_parent_projection']:
            self.assertEqual(capsules(normal['pg4706_'+suffix+'.py']),capsules(values['pg4714_'+suffix+'.py']))
        bundle=compiler.sha(compiler.PRIOR/'bundle.safe.json')
        self.assertTrue(require_bound(values['pg4714_native_refs.py'],bundle))
        # RO changes mode of the already-installed candidate, not another archive extraction.
        self.assertNotIn('BUNDLE_HASH',values['pg4714_input_preflight.py'])
        for name,raw in values.items():
            if name.endswith('.py'):self.assertEqual(0,check(raw,'<actual normal RO '+name+'>'))
        for path in ['api/api.jar','operations/batch.jar','api/lib/*','operations/lib/*']:
            self.assertIn('pg4432-release-v1/'+path,compiler.compiler())
        self.assertIn('pg4708-frozen-v1.safe.json',compiler.compiler())
        self.assertNotIn('pg3996',compiler.compiler())

    def test_unqualified_old_foreign_or_missing_post_does_not_admit_ro(self):
        original=json.loads((role.W/'pg4712-ssc299-unused-post-v1/manifest.safe.json').read_bytes())
        for key,value in [('candidateSource',role.CURRENT),('currentSource',role.SOURCE),
                          ('candidateManifestSha256','0'*64),('native64Preserved',False),
                          ('newTenReferencesReturnedNormally',False),('actualExit',False)]:
            bad=copy.deepcopy(original);bad['result'][key]=value
            with patch.object(role.unused,'qualify'),patch.object(role.json,'loads',return_value=bad):
                with self.subTest(key=key),self.assertRaises(ValueError):role.qualify()
        for path in [role.__file__,compiler.__file__,__file__]:self.assertEqual(0,checkPath(path))


if __name__=='__main__':unittest.main()
