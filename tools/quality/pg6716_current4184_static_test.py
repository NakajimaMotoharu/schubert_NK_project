import unittest
import json
import pg6716_current4184_static_join as p


class StaticSpanDefinitionTest(unittest.TestCase):
    def test_all154_new_spans_match_current_qualified_source(self):
        raw=json.loads((p.W/'pg6712-broker-parent-qualification-v3/findings.safe.json').read_bytes())
        old=p.load(p.PRIOR,p.PRIOR_SHA,p.OLD);pairs=p.ordered_pairs(old,raw)
        self.assertEqual((1404,1250),(len(raw),len(pairs)))
        changed=[r for r in raw if r['findingId'] not in pairs]
        self.assertEqual(154,len(changed))
        for row in changed:
            self.assertEqual(row['sourceSha256'],p.sha(p.ROOT/row['sourcePath']))
            actual=p.review_changed(row)
            self.assertIn(actual['status'],('REQUIRED_CONTRACT','CONTEXT_NOT_APPLICABLE'))
            self.assertTrue(actual['rawWarningRetained'])

    def test_no_blanket_new_context_or_rule(self):
        with self.assertRaisesRegex(ValueError,'eight individually'):
            p.review_changed(dict(sourcePath='Unknown.java',rule='AvoidCatchingGenericException'))
        with self.assertRaisesRegex(ValueError,'eight individually'):
            p.review_changed(dict(sourcePath='ApiBrokerContexts.java',rule='Unknown'))
        self.assertEqual(8,len(p.CONTEXTS))

    def test_global_raw_id_is_not_semantic_identity(self):
        old={k:'same' for k in p.prior.prior.SEMANTIC};old.update(findingId='old',rawXmlOrdinal=1,status='NOT_REVIEWED_CURRENT_SOURCE',reason='held operational scope')
        new=dict(old,findingId='new',rawXmlOrdinal=5)
        actual=p.bindings()['rebind_unchanged'](new,old)
        self.assertEqual('new',actual['findingId']);self.assertEqual('old',actual['priorFindingId'])
        self.assertEqual('NOT_REVIEWED_CURRENT_SOURCE',actual['status'])


if __name__=='__main__':unittest.main()
