import unittest
import pg6290_application_static_reviews as subject


class ApplicationBoundaries(unittest.TestCase):
    def test_twelve_spans_with_actual_source_and_no_new_business_requests(self):
        rows,value=subject.calculate()
        self.assertEqual(12,len(rows));self.assertEqual(12,len({r['findingId']for r in rows}))
        self.assertEqual(383,value['statusCounts']['NOT_REVIEWED_CURRENT_SOURCE'])
        self.assertEqual(115,value['statusCounts']['REQUIRED_CONTRACT'])
        self.assertFalse(value['F03Accepted']);self.assertEqual(0,value['testsExecuted'])
        for row in rows:
            self.assertTrue(row['sourcePath'].startswith('src/schubert-nk-api/'))
            self.assertTrue(row['plannedCurrentWholeCaseClasses'])
            self.assertEqual([],row['currentWholeCaseRefs']);self.assertTrue(row['currentWholeJoinPending'])
            self.assertFalse(row['actualRuntimeProven'])


if __name__=='__main__':unittest.main()
