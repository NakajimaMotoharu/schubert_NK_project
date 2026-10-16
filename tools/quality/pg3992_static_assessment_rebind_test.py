import inspect
import unittest
from pyflakes.api import check
import pg3992_static_assessment_rebind as assessment


class NarrowAssessment(unittest.TestCase):
    def test_only_one_unchanged_full_range_maps_not_changed_text_or_partial(self):
        self.assertEqual((3, 4), assessment.mapped_lines('a\nb\nc\n', 'new\na\nb\nc\n', 2, 3))
        for first, last in [(0, 1), (3, 2), (1, 4)]: self.assertIsNone(assessment.mapped_lines('a\nb\nc', 'a\nb\nc', first, last))
        self.assertIsNone(assessment.mapped_lines('a\nb\nc', 'a\nchanged\nc', 1, 3))
        self.assertIsNone(assessment.mapped_lines('a\nb\nc', 'a\ninsert\nb\nc', 1, 3))
        self.assertIsNone(assessment.mapped_lines('a\nb\na', 'a\nb\na', 1, 1))

    def test_current_complete_namespace_and_historical_proof_never_gate(self):
        raw = 'import difflib\n' + '\n'.join(inspect.getsource(f) for f in [assessment.require, assessment.mapped_lines, assessment.server])
        self.assertEqual(0, check(raw, '<narrow current source statements>')); compile(raw, '<narrow current source statements>', 'exec')
        for value in ['NO_FULL_SEMANTIC_EQUIVALENCE_FOR_CHANGED_SOURCE', 'NO_UNIQUE_CURRENT_SAME_RULE_MESSAGE_COORDINATE', 'STATEMENT_BYTES_NOT_ONE_UNCHANGED_BLOCK', "len(requalified) + len(held) == 304", "'F03Accepted': False", "'newTechnicalAssessments': 0"]: self.assertIn(value, raw)


if __name__ == '__main__': unittest.main()
