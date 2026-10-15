import ast
import unittest

import pg3434_current_outbox_candidate_sources as current
import pg3436_current_outbox_candidate_compile as compiler


class CurrentCandidateRoles(unittest.TestCase):
    def test_numeric_job_binding_never_rewrites_a_digest_fragment(self):
        original = 'a' * 30 + '74434' + 'b' * 29
        self.assertEqual(64, len(original))
        self.assertEqual("digest='" + original + "'", current.bind("digest='" + original + "'"))
        self.assertEqual('job=60559; other=x74434y; count=174434',
                         current.bind('job=74434; other=x74434y; count=174434'))

    def test_all_eighteen_namespaces_exact_current_and_candidate_roles(self):
        values = current.sources(); self.assertEqual(18, len(values))
        raw = '\n'.join(values.values())
        for marker in [current.CURRENT, current.SOURCE, current.CURRENT_BOM, current.BOM,
                       current.BEFORE, current.BOOT, current.TOOLS, 'pg3432-current-a9-before-view-v2']:
            self.assertIn(marker, raw)
        self.assertIn('/opt/schubert-nk/releases/0.1.0-PG3420', values['pg3434_input_preflight.py'])
        self.assertIn('/opt/schubert-nk/releases/0.1.0-PG2802', values['Pg3434UnusedStage.java'])
        for forbidden in [current.old.SOURCE, current.old.CURRENT, current.old.BEFORE, current.old.BOOT]:
            self.assertNotIn(forbidden, raw)
        self.assertEqual(current.BOOT.replace('-', ''), current.binding(values['pg3434_parent_receipt.py'])['boot'])

    def test_wrong_candidate_and_before_refused_without_operation(self):
        for value in [None, '', 'a' * 64, current.CURRENT_BOM]:
            with self.assertRaises(ValueError): current.sources(value)
        with self.assertRaises(ValueError): current.sources(current.BOM, 'b' * 64)

    def test_host_abi_uses_current_shared_classes_and_new_only_bundle(self):
        raw = compiler.compiler(); ast.parse(raw)
        for marker in ['pg3420-candidate-build-v1', 'pg3152-frozen-v1',
                       'pg3150-browser-business-owned-stop-tools-v1', 'pg2802-release-v1',
                       'pg3432-current-a9-before-view-v2', 'Pg3434OriginalTupleTest']:
            self.assertIn(marker, raw)
        for forbidden in ['pg2555-frozen', 'pg2654-release-v1', 'systemctl', 'daemon-reload']:
            self.assertNotIn(forbidden, raw)


if __name__ == '__main__':
    unittest.main()
