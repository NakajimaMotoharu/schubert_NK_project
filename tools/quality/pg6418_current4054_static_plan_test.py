import copy
import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
import pg6418_current4054_static_plan as subject


class Definition(unittest.TestCase):
    def test_actual1358_and_old14_stay_pending_not_pass(self):
        rows, value = subject.calculate()
        self.assertEqual(1358, len(rows))
        self.assertEqual({'SOURCE_REBOUND_CURRENT_WHOLE_PENDING': 1219, 'NOT_REVIEWED_CURRENT_SOURCE': 139}, value['statusCounts'])
        self.assertEqual(1205, value['strictReboundPriorDecided']); self.assertEqual(14, value['priorUnresolvedRetained'])
        self.assertFalse(value['F03Accepted']); self.assertEqual(0, value['testsExecuted'])
        for path in (subject.__file__, __file__):
            self.assertEqual(0, checkPath(path))

    def test_old_unresolved_cannot_be_promoted_by_missing_marker(self):
        rows = copy.deepcopy(subject.prior.load(subject.PRIOR, subject.PRIOR_SHA, subject.OLD))
        next(r for r in rows if r['status'] == 'SOURCE_REBOUND_CURRENT_WHOLE_PENDING')['wholeSourceQualifiedCaseBindingStillPending'] = False
        with patch.object(subject.prior, 'load', return_value=rows), self.assertRaisesRegex(ValueError, 'explicit prior unresolved'):
            subject.calculate()


if __name__ == '__main__':
    unittest.main()
