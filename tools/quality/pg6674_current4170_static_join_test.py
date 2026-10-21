import unittest
import pg6674_current4170_static_join as p


class OrdinaryStaticReviewTest(unittest.TestCase):
    def test_exact_multiline_header_not_a_nearby_body_or_comment(self):
        text='// catch (Error notCode) {}\ntry {} catch (RuntimeException\n | Error failure) {\n keep(failure);\n}\n'
        expected=['keep','(','failure',')',';']
        self.assertEqual(expected,p.catch_words(text,2));self.assertEqual(expected,p.catch_words(text,3))
        for line in (1,4,5,6):
            with self.assertRaises(ValueError):p.catch_words(text,line)
        self.assertEqual(['keep','(',')',';'],p.catch_words('try {} catch (Error failure) {keep();}',1))
        with self.assertRaises(ValueError):p.catch_words('try {} catch (Error a) {} try {} catch (Error b) {}',1)

    def test_current_all112_spans_reviewed_and_unsafe_secondary_stays_held(self):
        import json
        rows=json.loads((p.W/'pg6666-consumer-graph-qualification-v2/findings.safe.json').read_bytes())
        current=[r for r in rows if r['sourcePath'].rsplit('/',1)[-1].removesuffix('.java') in p.CONTEXTS]
        actual=[p.review_changed(r) for r in current]
        self.assertEqual(112,len(actual))
        held=[r for r in actual if r['status']=='NOT_REVIEWED_CURRENT_SOURCE']
        self.assertTrue(held)
        self.assertEqual({'BUG-1604'},{r['relatedBug'] for r in held})
        self.assertTrue(all(r['rawWarningRetained'] for r in actual))
        final=[r for r in actual if r['rule']=='DoNotThrowExceptionInFinally']
        self.assertEqual(1,len(final));self.assertEqual('REQUIRED_CONTRACT',final[0]['status'])

    def test_new_scope_not_blanket_approved_and_prior_identity_mapping_preserved(self):
        with self.assertRaises(ValueError):p.review_changed(dict(sourcePath='Unreviewed.java',rule='EmptyCatchBlock'))
        old={k:'same' for k in p.prior.SEMANTIC};old.update(findingId='old',rawXmlOrdinal=1,status='REQUIRED_CONTRACT',reason='prior')
        new=dict(old,findingId='new',rawXmlOrdinal=3,status='NOT_REVIEWED_CURRENT_SOURCE')
        actual=p.bindings()['rebind_unchanged'](new,old)
        self.assertEqual('new',actual['findingId']);self.assertEqual('old',actual['priorFindingId'])
        self.assertEqual('REQUIRED_CONTRACT',actual['status'])


if __name__=='__main__':unittest.main()
