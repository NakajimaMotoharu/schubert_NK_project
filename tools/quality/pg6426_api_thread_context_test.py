import copy
import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
import pg6426_api_thread_context as subject


class Definition(unittest.TestCase):
    def test_exact_two_rule_context_resolutions_no_dynamic_success(self):
        rows, changes, value = subject.calculate()
        self.assertEqual(1358, len(rows)); self.assertEqual(2, len(changes))
        self.assertEqual({'SOURCE_REBOUND_CURRENT_WHOLE_PENDING': 1217, 'NOT_REVIEWED_CURRENT_SOURCE': 134,
                          'REQUIRED_CONTRACT': 5, 'CONTEXT_NOT_APPLICABLE': 2}, value['statusCounts'])
        self.assertEqual(12, value['remainingMissingSemanticBindings']); self.assertEqual(0, value['testsExecuted'])
        self.assertTrue(all(r['staticContextPremiseOnly'] and r['currentWholeCaseRefs'] == [] and r['currentWholeJoinPending'] for r in changes))
        self.assertFalse(value['F03Accepted'])
        for path in (subject.__file__, __file__):
            self.assertEqual(0, checkPath(path))

    def test_absent_prior_pending_marker_or_one_missing_site_fails_closed(self):
        rows = copy.deepcopy(subject.load(subject.INPUT, subject.INPUT_SHA, subject.original_source()))
        selected = next(r for r in rows if r['sourcePath'] == subject.PATH and r['rule'] == 'DoNotUseThreads')
        selected['wholeSourceQualifiedCaseBindingStillPending'] = False
        with patch.object(subject, 'load', return_value=rows), self.assertRaisesRegex(ValueError, 'previously unresolved'):
            subject.calculate()
        reasons = dict(subject.REASONS); reasons.pop(87)
        with patch.object(subject, 'REASONS', reasons), self.assertRaisesRegex(ValueError, 'both exact|both'):
            # A missing source contract declaration must never authorize a partial resolution.
            subject.calculate()


if __name__ == '__main__':
    unittest.main()
