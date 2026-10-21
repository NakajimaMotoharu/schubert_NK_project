import copy
import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
import pg6342_application_boundary_static_reviews as subject


class Definition(unittest.TestCase):
    def test_exact11_current_unique_spans_without_selected_or_runtime_claim(self):
        rows,value=subject.calculate()
        self.assertEqual(11,len(rows));self.assertEqual(11,len({r['findingId']for r in rows}))
        self.assertEqual(332,value['statusCounts']['NOT_REVIEWED_CURRENT_SOURCE'])
        self.assertEqual(46,value['statusCounts']['REQUIRED_CONTRACT'])
        self.assertEqual(969,value['statusCounts']['SOURCE_REBOUND_CURRENT_WHOLE_PENDING'])
        self.assertEqual(0,value['testsExecuted']);self.assertFalse(value['F03Accepted'])
        for row in rows:
            self.assertEqual('REQUIRED_CONTRACT',row['status']);self.assertFalse(row['actualRuntimeProven'])
            self.assertTrue(row['currentWholeJoinPending']);self.assertEqual([],row['currentWholeCaseRefs'])
            self.assertTrue(row['plannedCurrentWholeCaseClasses'])
        for path in (subject.__file__,__file__):self.assertEqual(0,checkPath(path))

    def test_missing_one_application_boundary_rejected(self):
        spec=copy.deepcopy(subject.SPEC);del spec['ScenarioApplicationService'][(311,subject.G)]
        with patch.object(subject,'SPEC',spec),self.assertRaisesRegex(ValueError,'all11'):
            subject.calculate()


if __name__=='__main__':unittest.main()
