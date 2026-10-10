"""Independent literal current-profile and inherited finite negative contracts."""
import ast
import unittest
from pg1134_failed_recovery_sources import files, SOURCE, BOM, BASE_HASH


class SourcesTest(unittest.TestCase):
    def test_seven_file_closure_current_binding_and_sole_stop(self):
        result = files(); self.assertEqual(len(result), 7)
        java = result['Pg1134SingleApiRecovery.java']; refs = result['pg1134_single_api_refs.py']
        for text in [SOURCE, BOM, '0.1.0-PG1068', '343a5a1b-d064-47d5-88c2-31c36d7ba7a4',
                     'List.of("artemis.service")', 'original24TablesAnd604BatchPreserved',
                     'MaintenanceFileLock.create().tryExclusive', 'StartupAdmissionFile.create().tryExclusive']:
            self.assertIn(text, java)
        self.assertIn(BASE_HASH, refs); self.assertIn("ORDER=['artemis.service']", refs)
        for text in ['normalize_baseline()', "len(baseline['rows']['schubert.batch_runs'])==604",
                     'broker_policy.configuration(', 'baseline[\'unitFiles\']', "'ticks':3477622"]:
            self.assertIn(text, refs)
        for name, text in result.items():
            if name.endswith('.py'): ast.parse(text)
            for old in ['bbb6dc1276a4459da65143db3e4ee3f0', 'cc9ed874-7f4f-450e-a188-8de1e42c8441', '0.1.0-PG495']:
                self.assertNotIn(old, text)

    def test_parent_data_only_original_identity_and_no_expired_guard(self):
        result = files()
        for name in ['Pg1134IssuedApiRecovery.java', 'Pg1134SingleApiIntent.java']:
            text = result[name]
            for value in ['21f20c0cdbe34ce99431a55b10f92285', '242818', '3465834', 'owner.cleanup().isEmpty()']:
                self.assertIn(value, text)
            self.assertNotIn('.parentsGuard(', text)
        refs = result['pg1134_single_api_refs.py']
        for value in ['normal_terminal', 'broker_witness', 'metadata', 'configuration_fields',
                      "'MainPID'", 'stop-reserved.private', 'broker-manager.private.jsonl',
                      'REF_RELEASED', 'manager.UnrefUnit(u)', 'bus.close()']:
            self.assertIn(value, refs)

    def test_generated_startup_matrix_same_original_and_revoke_bytes(self):
        text = files()['pg1134_single_api_refs.py']
        tree = ast.parse(text)
        names = {'startup_preserved', 'canonical_invalid', 'kernel_actor', 'require'}
        defs = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
        env = {'STARTUP': '/run/schubert-nk/startup', 'revoked_phase': False}
        exec(compile(ast.Module(body=defs, type_ignores=[]), '<independent generated finite oracle>', 'exec'), env)
        raw = (b'NKEPOCH1\nstate=ISSUED\nboot_id=cbca8738-3b24-4090-b77c-bf029677cdd6\n'
               b'epoch_id=ecf22224-112b-46b5-a103-bde3aab63229\nrun_id=343a5a1b-d064-47d5-88c2-31c36d7ba7a4\n'
               b'cutoff_utc=2026-10-10T12:40:27.396847Z\nactivation_id=ada3f7ff-8287-48d7-9ba9-5cce71f61bd3\npermit_sha256=' + b'a' * 64 + b'\n')
        expected = raw.replace(b'state=ISSUED', b'state=INVALID').replace(b'permit_sha256=' + b'a' * 64, b'permit_sha256=-')
        self.assertEqual(env['canonical_invalid'](raw), expected)
        self.assertTrue(env['kernel_actor'](['253968'], ['', '']))
        for processes, children in [([], ['']), (['253968', 'other'], ['']), (['253968'], ['child']), (None, [])]:
            self.assertFalse(env['kernel_actor'](processes, children))
        for value in [None, b'', raw.replace(b'SS UED', b'ISSUED')[:-1], raw.replace(b'state=ISSUED', b'state=INVALID')]:
            with self.subTest(value=type(value).__name__), self.assertRaises(ValueError): env['canonical_invalid'](value)


if __name__ == '__main__': unittest.main()
