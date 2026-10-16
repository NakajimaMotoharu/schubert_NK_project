"""No normal success substitution; full current image and independent negative tuples."""
import ast
import hashlib
import unittest
import pg4444_failed_current_unused_sources as role
import pg4446_failed_current_unused_compile as compiler


class FailedCurrentEntry(unittest.TestCase):
    def test_all18_roles_keep_fresh_full_image_and_no_normal_parent_authority(self):
        values = role.sources(); self.assertEqual(18, len(values))
        refs = values['pg4444_native_refs.py']; java = values['Pg4444UnusedStage.java']
        self.assertIn("INV = 'bbcdb69957764d489a9c757b441542fd'", refs)
        self.assertIn('END = 151422334917', refs)
        self.assertIn(role.BEFORE, refs)
        self.assertIn('pg4440-failed-full-image-diagnosis-v1/canonical-before10.private.json', refs)
        self.assertIn('qualify_failed_parent(parent)', refs); self.assertIn('failed_completed(rows, done)', refs)
        self.assertNotIn('qualify_warning_parent', refs)
        self.assertIn('epoch.state()==StartupPermitRecords.State.INVALID && epoch.permitDigest().isEmpty()', java)
        self.assertIn('failedParent143DataOnly=true', java)
        self.assertNotIn('genuineParentNormalWarningOriginal=true', java)
        self.assertIn('refs.check("before")', java); self.assertIn('lease.confirmClosed()', java)
        # The embedded archive policy is unchanged, including no symlink/device/
        # traversal/extra files. Only new candidate identity/paths are rebound.
        old = role.previous.sources()['pg3982_native_refs.py']
        def policy(raw):
            return next(ast.literal_eval(n.value) for n in ast.walk(ast.parse(raw)) if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == 'CONTRACT' for t in n.targets))
        self.assertEqual(hashlib.sha256(policy(old).encode()).digest(), hashlib.sha256(policy(refs).encode()).digest())

    def test_current_failure_certificate_rejects_old_normal_or_wrong_state(self):
        namespace = {}; exec(role.parent_source(), namespace)
        expected = dict(role.proof()['parentFields'])
        self.assertEqual({'currentManagerGc':False,'normalUnit0or10':False,'stopAuthority':False,'failedParent143Confirmed':True}, namespace['qualify_failed_parent'](expected))
        for key, value in [('ExecMainStatus','10'), ('Result','success'), ('MainPID','795724'), ('Job','167140'), ('InvocationID','898f87b2f2c4406fb75011eb377dfb77'), ('ControlGroup','/foreign')]:
            changed = dict(expected); changed[key] = value
            with self.assertRaises(ValueError): namespace['qualify_failed_parent'](changed)
        with self.assertRaises(ValueError): namespace['qualify_failed_parent']({})

    def test_host_compile_uses_new_candidate_but_actual_current_jar_source(self):
        raw = compiler.compiler(); compile(raw, '<host current ABI>', 'exec')
        self.assertIn('pg4432-release-v1', raw); self.assertIn("old = W / 'pg3976-release-v1'", raw)
        self.assertIn('currentCompileJarSource', raw)
        self.assertIn('pg4444-failed-current-unused-tools-v1', str(compiler.TARGET))
        self.assertIn('pg4448-shared-manager-release-v1.tar', str(compiler.ARCHIVE))


if __name__ == '__main__':
    unittest.main()
