import copy
import unittest
from unittest.mock import patch
import pg6284_web_owned_static_reviews as subject


class ReviewScope(unittest.TestCase):
    def test_exact33_and_startup_compound_gap_left_unreviewed(self):
        rows,value=subject.calculate()
        self.assertEqual(33,len(rows));self.assertEqual(33,len({r['findingId']for r in rows}))
        self.assertEqual(445,value['statusCounts']['NOT_REVIEWED_CURRENT_SOURCE'])
        self.assertFalse(value['F03Accepted']);self.assertFalse(value['formalAccepted'])
        self.assertEqual(0,value['testsExecuted'])
        for row in rows:
            self.assertTrue(row['currentWholeJoinPending'])
            self.assertTrue(row['plannedCurrentWholeCaseClasses'])
            self.assertEqual([],row['currentWholeCaseRefs'])
            self.assertNotIn((row['sourcePath'].rsplit('/',1)[-1],row['beginline']),[('WebHttpServer.java',167),('WebHttpServer.java',172)])

    def test_incomplete_multiplicity_cannot_be_reported_as33(self):
        spec=copy.deepcopy(subject.SPEC);spec['WebHttpServer'].pop((112,subject.C))
        with patch.object(subject,'SPEC',spec),self.assertRaisesRegex(ValueError,'all33 explicit'):
            subject.calculate()


if __name__=='__main__':unittest.main()
