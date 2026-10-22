import json
import unittest
from unittest.mock import patch
import pg6788_current115_web_receivers as sql
import pg6790_current4197_web_static_join as static
import pg6792_sql58_web_jvm as jvm
import pg6794_current4197_web_trace as trace


class WebReaderDefinitionTest(unittest.TestCase):
    def test_current_all_raw_and_eighteen_changed_web_spans_reviewed(self):
        raw=json.loads((static.W/'pg6782-web-management-result-original-v1/findings.safe.json').read_bytes())
        old=static.base.load(static.PRIOR,static.PRIOR_SHA,static.OLD)
        pairs=static.base.ordered_pairs(old,raw);changed=[r for r in raw if r['findingId']not in pairs]
        self.assertEqual((1405,1387,18),(len(raw),len(pairs),len(changed)))
        self.assertEqual({'REQUIRED_CONTRACT','CONTEXT_NOT_APPLICABLE'},{static.review_changed(r)['status']for r in changed})
        self.assertEqual(13,len({(int(r['beginline']),r['rule'])for r in changed}))
        with self.assertRaises(ValueError):static.review_changed(dict(changed[0],beginline='1'))
        with self.assertRaises(ValueError):static.review_changed(dict(changed[0],sourceSha256='0'*64))

    def test_exact_future_scope_no_result_invention(self):
        self.assertTrue(callable(sql.definition()));self.assertTrue(callable(static.definition()))
        with patch.object(jvm,'SQLSHA',None):self.assertIsNone(jvm.definition().__globals__['SQLSHA'])
        d=trace.definitions('0'*64,'0'*64)
        self.assertIs(d['measurement'].__globals__,d['publish'].__globals__)
        self.assertIs(trace.read_qualified,d['measurement'].__globals__['read_qualified'])
        self.assertEqual(trace.SOURCE,d['measurement'].__globals__['SOURCE'])
        for value in ('PG6784-six-v1',4197,646,1669):self.assertIn(value,d['measurement'].__code__.co_consts)
        self.assertNotIn('PG6768-six-v1',d['measurement'].__code__.co_consts)


if __name__=='__main__':unittest.main()
