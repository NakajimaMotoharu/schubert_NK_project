import copy
import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
import pg6392_current4052_static_plan as subject


class Definition(unittest.TestCase):
    def test_actual1355_source_class_and_pending14_not_success(self):
        rows, value = subject.calculate()
        self.assertEqual(1355, len(rows))
        self.assertEqual({'SOURCE_REBOUND_CURRENT_WHOLE_PENDING': 1175, 'NOT_REVIEWED_CURRENT_SOURCE': 180}, value['statusCounts'])
        self.assertEqual(1161, value['strictReboundPriorDecided'])
        self.assertEqual(14, value['priorUnresolvedRetained'])
        self.assertFalse(value['F03Accepted']); self.assertEqual(0, value['testsExecuted'])
        for path in (subject.__file__, __file__):
            self.assertEqual(0, checkPath(path))

    def test_old_missing_semantic_cases_cannot_be_promoted(self):
        rows = copy.deepcopy(subject.prior.load(subject.PRIOR, subject.PRIOR_SHA, subject.OLD))
        next(r for r in rows if r['status'] == 'SOURCE_REBOUND_CURRENT_WHOLE_PENDING')['wholeSourceQualifiedCaseBindingStillPending'] = False
        with patch.object(subject.prior, 'load', return_value=rows), self.assertRaisesRegex(ValueError, 'explicit prior unresolved'):
            subject.calculate()


if __name__ == '__main__':
    unittest.main()
