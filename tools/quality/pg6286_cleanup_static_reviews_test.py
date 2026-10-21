import unittest
import pg6286_cleanup_static_reviews as subject


class ExactBatchScopes(unittest.TestCase):
    def test_all32_and_transaction_168_not_blanket_approved(self):
        rows,value=subject.calculate()
        self.assertEqual(32,len(rows));self.assertEqual(32,len({r['findingId']for r in rows}))
        self.assertEqual(413,value['statusCounts']['NOT_REVIEWED_CURRENT_SOURCE'])
        self.assertEqual(91,value['statusCounts']['REQUIRED_CONTRACT'])
        self.assertEqual(0,value['testsExecuted']);self.assertFalse(value['F03Accepted'])
        for row in rows:
            self.assertTrue(row['sourcePath'].startswith('src/schubert-nk-batch/'))
            self.assertTrue(row['plannedCurrentWholeCaseClasses'])
            self.assertTrue(row['currentWholeJoinPending']);self.assertEqual([],row['currentWholeCaseRefs'])
            self.assertNotEqual(('LogCleanupService.java',168),(row['sourcePath'].rsplit('/',1)[-1],row['beginline']))


if __name__=='__main__':unittest.main()
