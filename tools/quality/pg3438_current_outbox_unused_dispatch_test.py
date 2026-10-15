import ast
import inspect
import json
import types
import unittest

import pg3438_current_outbox_unused_dispatch as current


class NewOnlyUnusedDispatch(unittest.TestCase):
    def test_standalone_stage_uses_current_boot_not_historical_template(self):
        self.assertIn(current.role.BOOT, current.STAGE)
        self.assertNotIn(current.role.old.BOOT, current.STAGE)
        node = next(n for n in ast.parse(current.STAGE).body if isinstance(n, ast.Assert) and 'boot_id' in ast.unparse(n))
        code = compile(ast.Module(body=[node], type_ignores=[]), '<actual isolated stage boot guard>', 'exec')
        for boot in [current.role.BOOT, current.role.old.BOOT, '00000000-0000-0000-0000-000000000000']:
            path = types.SimpleNamespace(read_text=lambda: boot)
            ns = {'pathlib': types.SimpleNamespace(Path=lambda _: path)}
            if boot == current.role.BOOT: exec(code, ns)
            else:
                with self.assertRaises(AssertionError): exec(code, ns)

    def test_resume_is_reserved_separately_and_reauthenticates_without_upload_replay(self):
        raw = inspect.getsource(current.stage_resume); tree = ast.parse(raw)
        self.assertNotIn('scp', [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant)])
        for marker in ['pg3438-stage-v1.safe.json', "b'1\\n'", 'pg3438-stage-v2',
                       'originalUploadsReauthenticatedAndReused', 'INPUTS=', 'sourceQualified', 'timeout=120']:
            self.assertIn(marker, raw)
        self.assertIn('StrictHostKeyChecking=yes', current.SSH)

    def test_actual_roles_new_paths_and_unchanged_all_scope_guards(self):
        candidate = json.loads((current.W / 'pg3420-candidate-build-v1.safe.json').read_bytes())
        before = current.before_record(); ns = current.runtime_namespace(candidate, before)
        self.assertEqual(current.role.SOURCE, ns['SOURCE'])
        self.assertEqual(current.role.BOM, ns['DIGEST'])
        self.assertEqual(current.role.BEFORE, ns['BASELINE_SHA'])
        raw = current.source(); compile(raw, '<new stage/place source>', 'exec')
        for marker in ['pg3436-frozen', 'pg3438-stage-v2.exit', 'pg3438-fixed-stage-v1',
                       current.role.ARCHIVE, 'pg3420-manifest-v1.sig', '0.1.0-PG2802',
                       '0.1.0-PG3420', current.role.SOURCE,
                       'reserved actual action must not be replayed', 'unusedPlacementOnly']:
            self.assertIn(marker, raw)
        self.assertIn(current.role.TOOLS, current.STAGE)
        for old in ['pg2659-frozen', 'pg2656-current-a79-before', '0.1.0-PG2512', '2f7ca23be804567a5d9a61636cf4c1d4ec96fcd0']:
            self.assertNotIn(old, raw)

    def test_missing_current_completion_or_fake_candidate_is_refused(self):
        candidate = json.loads((current.W / 'pg3420-candidate-build-v1.safe.json').read_bytes())
        before = current.before_record()
        for wrong in [{**before, 'genuineCompletion': None}, {**before, 'runtimeAlreadyRetired': False},
                      {**before, 'dataOnlyNotRuntimeAuthority': False}]:
            with self.assertRaises(ValueError): current.runtime_namespace(candidate, wrong)
        with self.assertRaises(ValueError): current.runtime_namespace({**candidate, 'signatureVerified': False}, before)


if __name__ == '__main__':
    unittest.main()
