import unittest
import pg3542_current_criteria_revalidation as review


class ExplicitSourceReviewBoundaries(unittest.TestCase):
    def test_cleanup_guard_only_and_no_expected_input_assertion_drift(self):
        path='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/MediaControllerTest.java'
        old=b'@AfterAll void stop() {\n    db.stop();\n}\nvoid oracle() { assertEquals(7, actual()); }'
        new=old.replace(b'    db.stop();',b'    if (db != null) db.stop();')
        self.assertEqual('EXACT_BYTES',review.cleanup_only(old,old,path))
        self.assertEqual('AFTERALL_NULL_GUARD_ONLY_EXPECTATIONS_INPUT_ASSERTIONS_UNCHANGED',review.cleanup_only(old,new,path))
        for candidate,target in [(new.replace(b'assertEquals(7',b'assertEquals(8'),path),
                                 (new,path+'Other'),(new+b'\nvoid extra(){}',path)]:
            with self.subTest(path=target),self.assertRaises(ValueError):review.cleanup_only(old,candidate,target)

    def test_normative_body_byte_exact_and_only_reviewed_prepend(self):
        old=b'# Original\n\n## Required\ncoverage100 and no exclusions\n'
        new=b'# Original\n\n## SSC-285\nSpecific fixed owner profile\n\n'+old.split(b'\n\n',1)[1]
        self.assertEqual(64,len(review.prepend_only(old,new,'## SSC-285')))
        for candidate in [new.replace(b'coverage100',b'coverage90'),new.replace(b'## SSC-285',b'## Arbitrary'),
                          new.replace(b'Specific fixed owner profile',b'Specific\n## Another')]:
            with self.assertRaises(ValueError):review.prepend_only(old,candidate,'## SSC-285')

    def test_all17_actual_individual_criteria_and_dependencies(self):
        actual=review.revalidate()
        self.assertEqual(review.EXPECTED,set(actual['rows']))
        self.assertEqual(51,actual['criteriaRevalidated'])
        self.assertEqual(0,actual['newLeafCredit'])
        self.assertFalse(actual['WbsSourceSwitchApplied'])
        self.assertEqual('WBS-P006-02',actual['onlyPhysicalChange'][0]['owner'])
        self.assertEqual(0,actual['rows']['WBS-P002-01']['sharedReferences'][0]['referenceCost'])


if __name__=='__main__':unittest.main()
