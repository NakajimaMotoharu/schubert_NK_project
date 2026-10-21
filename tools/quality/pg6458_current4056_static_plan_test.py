import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
import pg6458_current4056_static_plan as subject


class Definition(unittest.TestCase):
    def test_exact1361_unchanged_reasons_and_twelve_semantic_gaps_retained(self):
        rows, value = subject.calculate()
        self.assertEqual(1361, len(rows))
        # Morning's three previously context-only thread sites also require fresh review:
        # the owning class changed, even though the J2EE premise may remain inapplicable.
        # 50 original spans + 3 new diagnostic spans + 3 invalidated contexts + 11 held = 67.
        self.assertEqual({'SOURCE_REBOUND_CURRENT_WHOLE_PENDING': 1294,
                          'NOT_REVIEWED_CURRENT_SOURCE': 67}, value['statusCounts'])
        self.assertEqual(1282, value['strictReboundPriorDecided'])
        self.assertEqual(12, value['priorUnresolvedRetained'])
        self.assertFalse(value['F03Accepted'])
        self.assertEqual(0, value['testsExecuted'])
        for path in (subject.__file__, __file__):
            self.assertEqual(0, checkPath(path))

    def test_unbound_prior_manifest_cannot_become_current_success(self):
        with patch.object(subject, 'PRIOR_SHA', 'f'*64), self.assertRaises(ValueError):
            subject.calculate()


if __name__ == '__main__':
    unittest.main()
