import json
import unittest

import pg3438_current_outbox_unused_dispatch as current


class NewOnlyUnusedDispatch(unittest.TestCase):
    def test_actual_roles_new_paths_and_unchanged_all_scope_guards(self):
        candidate = json.loads((current.W / 'pg3420-candidate-build-v1.safe.json').read_bytes())
        before = current.before_record(); ns = current.runtime_namespace(candidate, before)
        self.assertEqual(current.role.SOURCE, ns['SOURCE'])
        self.assertEqual(current.role.BOM, ns['DIGEST'])
        self.assertEqual(current.role.BEFORE, ns['BASELINE_SHA'])
        raw = current.source(); compile(raw, '<new stage/place source>', 'exec')
        for marker in ['pg3436-frozen', 'pg3438-stage-v1.exit', 'pg3438-fixed-stage-v1',
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
