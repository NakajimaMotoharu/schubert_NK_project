import unittest
import pg6288_group_lookup_static_reviews as subject


class StandaloneLookup(unittest.TestCase):
    def test_all18_without_executing_lookup_or_granting_runtime_authority(self):
        rows,value=subject.calculate()
        self.assertEqual(18,len(rows));self.assertEqual(18,len({r['findingId']for r in rows}))
        self.assertEqual({'NOT_REVIEWED_CURRENT_SOURCE':395,'SOURCE_REBOUND_CURRENT_WHOLE_PENDING':846,
            'REQUIRED_CONTRACT':103,'CONTEXT_NOT_APPLICABLE':6},value['statusCounts'])
        self.assertEqual(0,value['testsExecuted']);self.assertFalse(value['formalAccepted']);self.assertFalse(value['F03Accepted'])
        self.assertEqual(6,len([r for r in rows if r.get('staticContextPremiseOnly')]))
        for row in rows:
            self.assertTrue(row['sourcePath'].endswith('/ConfigurationGroupResolver.java'))
            self.assertEqual([],row['currentWholeCaseRefs']);self.assertTrue(row['currentWholeJoinPending'])
            self.assertFalse(row['actualRuntimeProven'])


if __name__=='__main__':unittest.main()
