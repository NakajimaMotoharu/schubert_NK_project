"""Independent old/new approval and canonical invalid-epoch vectors, no Root authority."""
import ast
import copy
import hashlib
import json
import unittest
import pg4540_failed_current_publication_sources as p


class FiniteFailedData(unittest.TestCase):
    def test_real_readonly_post_and_old_normal_native_claim_rejected(self):
        v=json.loads((p.W/'pg4534-failed-current-ro-post-v1/manifest.safe.json').read_bytes());self.assertEqual(v['result'],p.qualify_result(v))
        for key,value in [('candidateHostReadonlyVerified',False),('oldParentNormal',True),('candidateNativeCredit',True),('formalAccepted',True)]:
            bad=copy.deepcopy(v);bad['result'][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):p.qualify_result(bad)

    def test_independent_approval_and_epoch_vectors_match_actual_finite_oracle(self):
        values=p.sources();raw=values['pg4540_ordinary_publication_contract.py'];tree=ast.parse(raw)
        nodes=[n for n in tree.body if isinstance(n,(ast.Assign,ast.FunctionDef))]
        ns={'hashlib':hashlib};import uuid;import stat;ns.update(uuid=uuid,stat=stat)
        exec(compile(ast.Module(body=nodes,type_ignores=[]),'<actual finite oracle constants>','exec'),ns)
        old=b'NKRELEASEAPPROVAL1\nversion=0.1.0-PG3976\nmanifest_sha256=0a409301e552d8019440edcbf096ad9b20c15b35c0ee6472cd9c4cef65bd8dab\n'
        new=b'NKRELEASEAPPROVAL1\nversion=0.1.0-PG4432\nmanifest_sha256=93807abdd4db24ad300b93d95d844ea21e64487dc5cf24b815c15db34305d3de\n'
        self.assertEqual(old,ns['OLD_APPROVAL']);self.assertEqual(new,ns['NEW_APPROVAL'])
        fresh='11111111-2222-4333-8444-555555555555'
        expected=(b'NKEPOCH1\nstate=INVALID\nboot_id=79a3260a-e16d-42bf-942a-b914ed144c28\nepoch_id=11111111-2222-4333-8444-555555555555\n'
          b'run_id=b1ba37cb-9b2b-469b-a5f2-b0e6d8c97cd1\ncutoff_utc=2026-10-16T11:32:53.943173Z\nactivation_id=8314450e-0dd5-4986-875c-81f73e1b50b2\npermit_sha256=-\n')
        self.assertEqual(expected,ns['epoch_bytes'](fresh));ns['canonical_epoch'](expected)
        for bad in [None,'unknown','79a3260a-e16d-42bf-942a-b914ed144c28','b1ba37cb-9b2b-469b-a5f2-b0e6d8c97cd1','8314450e-0dd5-4986-875c-81f73e1b50b2']:
            with self.subTest(bad=bad),self.assertRaises(ValueError):ns['epoch_bytes'](bad)

    def test_all24_full_failed_parent_and_java_transition_fixtures_are_explicit(self):
        v=p.sources();self.assertEqual(24,len(v));java=v[p.CLASS+'.java'];self.assertIn('StartupPermitRecords.State.INVALID && epoch.permitDigest().isEmpty()',java)
        self.assertIn('!fresh.equals(old.epoch())',java);self.assertIn('failedParent143DataOnly=true',java)
        transition=v['Pg4540TransitionTest.java'];self.assertIn('invalidExpected=null;Pg4540OrdinaryPublication.transitionOriginal(e(StartupPermitRecords.State.INVALID',transition)
        self.assertIn('reject(e(StartupPermitRecords.State.ISSUED,BOOT,FRESH,ACTIVATION),done)',transition);self.assertIn('checks!=14',transition)
        native=v['pg4540_native_refs.py'];self.assertIn('failed_completed(rows, done)',native);self.assertNotIn('qualify_warning_parent',native)
        self.assertIn("INV = 'bbcdb69957764d489a9c757b441542fd'",native);self.assertIn("set(('Id',",native)


if __name__=='__main__':unittest.main()
